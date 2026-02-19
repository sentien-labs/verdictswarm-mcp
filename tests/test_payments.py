"""Tests for Solana payment verification, auth, and pricing."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from verdictswarm_mcp.auth import authenticate, reset_free_tier_counts
from verdictswarm_mcp.config import TOOL_PRICING, USDC_MINT
from verdictswarm_mcp.payments import (
    _verified_signatures,
    clear_verified_signatures,
    get_payment_instructions,
    verify_solana_payment,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WALLET = "TestWallet111111111111111111111111111111111"
SENDER = "SenderWallet11111111111111111111111111111111"
TX_SIG = "5xTestSignature1111111111111111111111111111111111111111111111111111111"

VALID_TX_RESPONSE = {
    "result": {
        "meta": {
            "err": None,
            "innerInstructions": [],
            "postTokenBalances": [
                {
                    "accountIndex": 2,
                    "mint": USDC_MINT,
                    "owner": WALLET,
                    "uiTokenAmount": {"uiAmount": 0.10, "decimals": 6},
                }
            ],
        },
        "transaction": {
            "message": {
                "accountKeys": [
                    {"pubkey": SENDER},
                    {"pubkey": "SomeProgram111111111111111111111111111111111"},
                    {"pubkey": "DestTokenAccount111111111111111111111111111"},
                ],
                "instructions": [
                    {
                        "parsed": {
                            "type": "transferChecked",
                            "info": {
                                "mint": USDC_MINT,
                                "destination": "DestTokenAccount111111111111111111111111111",
                                "authority": SENDER,
                                "tokenAmount": {"uiAmount": 0.10, "decimals": 6},
                            },
                        }
                    }
                ],
            }
        },
    }
}


@pytest.fixture(autouse=True)
def reset_state():
    """Reset payment and auth state between tests."""
    clear_verified_signatures()
    reset_free_tier_counts()
    yield
    clear_verified_signatures()
    reset_free_tier_counts()


# ---------------------------------------------------------------------------
# get_payment_instructions
# ---------------------------------------------------------------------------


def test_get_payment_instructions_scan_token():
    with patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET):
        info = get_payment_instructions("scan_token")
    assert info["amount_usdc"] == 0.10
    assert info["usdc_mint"] == USDC_MINT
    assert info["wallet"] == WALLET
    assert info["tool"] == "scan_token"
    assert "instructions" in info


def test_get_payment_instructions_get_quick_score():
    with patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET):
        info = get_payment_instructions("get_quick_score")
    assert info["amount_usdc"] == 0.02


def test_get_payment_instructions_compare_tokens():
    with patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET):
        info = get_payment_instructions("compare_tokens")
    assert info["amount_usdc"] == 0.15


def test_get_payment_instructions_unknown_tool():
    with patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET):
        info = get_payment_instructions("unknown_tool")
    assert info["amount_usdc"] == 0.0


# ---------------------------------------------------------------------------
# verify_solana_payment — mock RPC
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_payment_success():
    with (
        patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET),
        patch("verdictswarm_mcp.payments._fetch_transaction", AsyncMock(return_value=VALID_TX_RESPONSE["result"])),
    ):
        result = await verify_solana_payment(TX_SIG, expected_amount=0.10)
    assert result["verified"] is True
    assert result["amount_usdc"] == 0.10
    assert result["sender"] == SENDER


@pytest.mark.asyncio
async def test_verify_payment_insufficient_amount():
    with (
        patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET),
        patch("verdictswarm_mcp.payments._fetch_transaction", AsyncMock(return_value=VALID_TX_RESPONSE["result"])),
    ):
        result = await verify_solana_payment(TX_SIG, expected_amount=0.50)
    assert result["verified"] is False
    assert "Insufficient payment" in result["error"]
    assert result["amount_usdc"] == 0.10


@pytest.mark.asyncio
async def test_verify_payment_tx_not_found():
    with (
        patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET),
        patch("verdictswarm_mcp.payments._fetch_transaction", AsyncMock(return_value=None)),
    ):
        result = await verify_solana_payment(TX_SIG, expected_amount=0.10)
    assert result["verified"] is False
    assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_verify_payment_no_signature():
    result = await verify_solana_payment("", expected_amount=0.10)
    assert result["verified"] is False
    assert "No transaction signature" in result["error"]


@pytest.mark.asyncio
async def test_verify_payment_no_wallet_configured():
    with patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", ""):
        result = await verify_solana_payment(TX_SIG, expected_amount=0.10)
    assert result["verified"] is False
    assert "VS_PAYMENT_WALLET" in result["error"]


# ---------------------------------------------------------------------------
# Replay protection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_replay_protection():
    with (
        patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET),
        patch("verdictswarm_mcp.payments._fetch_transaction", AsyncMock(return_value=VALID_TX_RESPONSE["result"])),
    ):
        first = await verify_solana_payment(TX_SIG, expected_amount=0.10)
        assert first["verified"] is True

        # Second use of the same signature should fail
        second = await verify_solana_payment(TX_SIG, expected_amount=0.10)
    assert second["verified"] is False
    assert "replay" in second["error"].lower()


def test_clear_verified_signatures():
    _verified_signatures.add("test_sig")
    assert "test_sig" in _verified_signatures
    clear_verified_signatures()
    assert len(_verified_signatures) == 0


# ---------------------------------------------------------------------------
# USDC transfer detection — wrong mint ignored
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_payment_wrong_mint_not_accepted():
    tx_wrong_mint = {
        "meta": {
            "err": None,
            "innerInstructions": [],
            "postTokenBalances": [],
        },
        "transaction": {
            "message": {
                "accountKeys": [{"pubkey": SENDER}, {"pubkey": "DestTokenAccount"}],
                "instructions": [
                    {
                        "parsed": {
                            "type": "transferChecked",
                            "info": {
                                "mint": "WrongMint1111111111111111111111111111111111",
                                "destination": "DestTokenAccount",
                                "authority": SENDER,
                                "tokenAmount": {"uiAmount": 1.0, "decimals": 6},
                            },
                        }
                    }
                ],
            }
        },
    }
    with (
        patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET),
        patch("verdictswarm_mcp.payments._fetch_transaction", AsyncMock(return_value=tx_wrong_mint)),
    ):
        result = await verify_solana_payment(TX_SIG, expected_amount=0.10)
    assert result["verified"] is False
    assert "No USDC transfer" in result["error"]


# ---------------------------------------------------------------------------
# Dual auth — authenticate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_valid_api_key():
    with patch("verdictswarm_mcp.auth.VS_API_KEY", "secret-key"):
        result = await authenticate("scan_token", api_key="secret-key")
    assert result is None


@pytest.mark.asyncio
async def test_auth_invalid_api_key():
    with patch("verdictswarm_mcp.auth.VS_API_KEY", "secret-key"):
        result = await authenticate("scan_token", api_key="wrong-key")
    assert result is not None
    assert result["error"] == "invalid_api_key"


@pytest.mark.asyncio
async def test_auth_valid_payment():
    with (
        patch("verdictswarm_mcp.payments.VS_PAYMENT_WALLET", WALLET),
        patch("verdictswarm_mcp.payments._fetch_transaction", AsyncMock(return_value=VALID_TX_RESPONSE["result"])),
        patch("verdictswarm_mcp.auth.VS_API_KEY", ""),
    ):
        result = await authenticate("scan_token", tx_signature=TX_SIG)
    assert result is None


@pytest.mark.asyncio
async def test_auth_invalid_payment():
    with (
        patch("verdictswarm_mcp.payments._fetch_transaction", AsyncMock(return_value=None)),
        patch("verdictswarm_mcp.auth.VS_API_KEY", ""),
    ):
        result = await authenticate("scan_token", tx_signature=TX_SIG)
    assert result is not None
    assert result["error"] == "payment_verification_failed"
    assert "payment_instructions" in result


@pytest.mark.asyncio
async def test_auth_no_auth_returns_instructions():
    with patch("verdictswarm_mcp.auth.VS_API_KEY", ""):
        result = await authenticate("scan_token")
    assert result is not None
    assert result["error"] == "authentication_required"
    assert "payment_instructions" in result
    assert result["payment_instructions"]["tool"] == "scan_token"


# ---------------------------------------------------------------------------
# Free tier rate limiting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_free_tier_allows_up_to_limit():
    with patch("verdictswarm_mcp.auth.VS_API_KEY", ""):
        for _ in range(10):
            result = await authenticate("get_quick_score", client_id="agent-1")
            assert result is None, f"Expected None but got {result}"


@pytest.mark.asyncio
async def test_free_tier_blocks_after_limit():
    with patch("verdictswarm_mcp.auth.VS_API_KEY", ""):
        for _ in range(10):
            await authenticate("get_quick_score", client_id="agent-2")
        result = await authenticate("get_quick_score", client_id="agent-2")
    assert result is not None
    assert result["error"] == "free_tier_limit_exceeded"
    assert result["daily_limit"] == 10


@pytest.mark.asyncio
async def test_free_tier_separate_per_client():
    with patch("verdictswarm_mcp.auth.VS_API_KEY", ""):
        # Use up agent-3's limit
        for _ in range(10):
            await authenticate("get_quick_score", client_id="agent-3")

        # agent-4 should still be allowed
        result = await authenticate("get_quick_score", client_id="agent-4")
    assert result is None


@pytest.mark.asyncio
async def test_free_tier_only_for_get_quick_score():
    """Non-free-tier tools require auth even with no calls made."""
    with patch("verdictswarm_mcp.auth.VS_API_KEY", ""):
        result = await authenticate("scan_token", client_id="agent-5")
    assert result is not None
    assert result["error"] == "authentication_required"


# ---------------------------------------------------------------------------
# Pricing table
# ---------------------------------------------------------------------------


def test_tool_pricing_values():
    assert TOOL_PRICING["scan_token"] == 0.10
    assert TOOL_PRICING["get_quick_score"] == 0.02
    assert TOOL_PRICING["check_rug_risk"] == 0.05
    assert TOOL_PRICING["analyze_contract"] == 0.10
    assert TOOL_PRICING["compare_tokens"] == 0.15
    # Free tools
    assert TOOL_PRICING["get_pricing"] == 0.0
    assert TOOL_PRICING["verify_payment"] == 0.0
