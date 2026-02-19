"""Solana USDC payment verification for VerdictSwarm MCP agent micropayments."""
from __future__ import annotations

import base64
import logging
from typing import Any

import httpx

from .config import SOLANA_RPC_URL, TOOL_PRICING, USDC_MINT, VS_PAYMENT_WALLET

logger = logging.getLogger(__name__)

# In-memory replay protection: set of verified tx signatures
_verified_signatures: set[str] = set()


def get_payment_instructions(tool_name: str) -> dict[str, Any]:
    """Return payment instructions for the calling agent.

    Returns a dict with wallet address, required amount, USDC mint,
    and human-readable instructions.
    """
    amount = TOOL_PRICING.get(tool_name, 0.0)
    return {
        "wallet": VS_PAYMENT_WALLET,
        "amount_usdc": amount,
        "usdc_mint": USDC_MINT,
        "network": "solana-mainnet",
        "instructions": (
            f"Send {amount} USDC to {VS_PAYMENT_WALLET} on Solana mainnet. "
            f"USDC mint: {USDC_MINT}. "
            f"After sending, call verify_payment or pass tx_signature to the tool."
        ),
        "tool": tool_name,
    }


async def verify_solana_payment(
    tx_signature: str,
    expected_amount: float,
    *,
    rpc_url: str = SOLANA_RPC_URL,
) -> dict[str, Any]:
    """Verify a Solana USDC payment transaction.

    Queries the Solana RPC to confirm:
    - Transaction exists and is finalized
    - A USDC SPL token transfer occurred
    - Destination matches VS_PAYMENT_WALLET
    - Amount is >= expected_amount (in USDC, adjusted for 6 decimals)

    Returns dict with:
    - verified: bool
    - error: str (if not verified)
    - amount_usdc: float (actual transferred amount)
    - sender: str (source wallet)
    """
    if not tx_signature:
        return {"verified": False, "error": "No transaction signature provided."}

    if not VS_PAYMENT_WALLET:
        return {"verified": False, "error": "Payment wallet not configured (VS_PAYMENT_WALLET)."}

    # Replay protection
    if tx_signature in _verified_signatures:
        return {"verified": False, "error": "Transaction signature already used (replay protection)."}

    tx_data = await _fetch_transaction(tx_signature, rpc_url=rpc_url)
    if tx_data is None:
        return {"verified": False, "error": "Transaction not found or not finalized on Solana."}

    result = _extract_usdc_transfer(tx_data, expected_amount)
    if result.get("verified"):
        _verified_signatures.add(tx_signature)

    return result


async def _fetch_transaction(tx_signature: str, *, rpc_url: str) -> dict[str, Any] | None:
    """Fetch transaction details from Solana RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_signature,
            {
                "encoding": "jsonParsed",
                "commitment": "finalized",
                "maxSupportedTransactionVersion": 0,
            },
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(rpc_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        logger.warning("Solana RPC error: %s", exc)
        return None

    result = data.get("result")
    if not result:
        return None
    # Check transaction was not an error
    if result.get("meta", {}).get("err") is not None:
        return None
    return result


def _extract_usdc_transfer(tx_data: dict[str, Any], expected_amount: float) -> dict[str, Any]:
    """Parse jsonParsed transaction to find a USDC transfer to our wallet."""
    meta = tx_data.get("meta", {})
    transaction = tx_data.get("transaction", {})
    message = transaction.get("message", {})

    # Walk through all instructions looking for SPL token transfer to our wallet
    instructions = message.get("instructions", [])
    inner_instructions_list = meta.get("innerInstructions", [])

    all_instructions: list[dict[str, Any]] = list(instructions)
    for inner in inner_instructions_list:
        all_instructions.extend(inner.get("instructions", []))

    for ix in all_instructions:
        parsed = ix.get("parsed")
        if not isinstance(parsed, dict):
            continue

        ix_type = parsed.get("type", "")
        info = parsed.get("info", {})

        # Accept transfer and transferChecked instruction types
        if ix_type not in ("transfer", "transferChecked"):
            continue

        # For transferChecked the mint is directly available
        mint = info.get("mint", "")
        if ix_type == "transferChecked" and mint != USDC_MINT:
            continue

        destination = info.get("destination", "")
        if not _wallet_matches(destination, VS_PAYMENT_WALLET, meta, message):
            continue

        # Amount: transferChecked uses tokenAmount.uiAmount, transfer uses amount (raw lamports-like)
        if ix_type == "transferChecked":
            token_amount = info.get("tokenAmount", {})
            amount_usdc = float(token_amount.get("uiAmount", 0) or 0)
        else:
            # raw amount / 10^6 for USDC (6 decimals)
            raw = int(info.get("amount", 0) or 0)
            amount_usdc = raw / 1_000_000

        sender = info.get("authority", info.get("source", "unknown"))

        if amount_usdc < expected_amount:
            return {
                "verified": False,
                "error": f"Insufficient payment: got {amount_usdc} USDC, need {expected_amount} USDC.",
                "amount_usdc": amount_usdc,
                "sender": sender,
            }

        return {
            "verified": True,
            "amount_usdc": amount_usdc,
            "sender": sender,
            "destination": destination,
        }

    return {
        "verified": False,
        "error": f"No USDC transfer to {VS_PAYMENT_WALLET} found in transaction.",
    }


def _wallet_matches(
    destination_token_account: str,
    owner_wallet: str,
    meta: dict[str, Any],
    message: dict[str, Any],
) -> bool:
    """Check if a destination token account belongs to our payment wallet.

    The destination in SPL transfers is often a token account (ATA), not the owner wallet.
    We check the post-token-balances to map token accounts back to their owners.
    """
    if destination_token_account == owner_wallet:
        return True

    # Check post token balances for owner mapping
    post_balances = meta.get("postTokenBalances", [])
    account_keys = message.get("accountKeys", [])

    for balance in post_balances:
        account_index = balance.get("accountIndex", -1)
        balance_owner = balance.get("owner", "")
        mint = balance.get("mint", "")

        if mint != USDC_MINT:
            continue
        if balance_owner != owner_wallet:
            continue

        # Get the account pubkey at this index
        if account_index < len(account_keys):
            key_entry = account_keys[account_index]
            pubkey = key_entry if isinstance(key_entry, str) else key_entry.get("pubkey", "")
            if pubkey == destination_token_account:
                return True

    return False


def clear_verified_signatures() -> None:
    """Clear the replay-protection cache (for testing only)."""
    _verified_signatures.clear()
