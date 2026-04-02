"""Dual authentication: API key OR Solana USDC micropayment."""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date
from typing import Any

from .config import FREE_TIER_LIFETIME_LIMIT, TOOL_PRICING, VS_API_KEY
from .payments import get_payment_instructions, verify_solana_payment

logger = logging.getLogger(__name__)

# Free tier rate limiting: {(client_id, date_str): call_count}
_free_tier_counts: dict[tuple[str, str], int] = defaultdict(int)

# Tools available on the free tier (no auth required, subject to rate limit)
FREE_TIER_TOOLS: frozenset[str] = frozenset({"get_quick_score"})


def _today() -> str:
    return date.today().isoformat()


def check_free_tier(tool_name: str, client_id: str) -> dict[str, Any] | None:
    """Check if the call is allowed under the free tier quota.

    Returns None if allowed, or an error dict if the limit is exceeded.
    Only applies to FREE_TIER_TOOLS.
    """
    if tool_name not in FREE_TIER_TOOLS:
        return None  # Not a free-tier tool; caller must authenticate

    key = (client_id, _today())
    count = _free_tier_counts[key]
    if count >= FREE_TIER_LIFETIME_LIMIT:
        return {
            "error": "free_tier_limit_exceeded",
            "message": (
                f"Free tier limit of {FREE_TIER_LIFETIME_LIMIT} calls/day for '{tool_name}' exceeded. "
                "Provide an API key or pay per call via tx_signature."
            ),
            "daily_limit": FREE_TIER_LIFETIME_LIMIT,
            "payment_instructions": get_payment_instructions(tool_name),
        }
    _free_tier_counts[key] += 1
    return None


async def authenticate(
    tool_name: str,
    *,
    api_key: str | None = None,
    tx_signature: str | None = None,
    client_id: str = "anonymous",
) -> dict[str, Any] | None:
    """Authenticate a tool call via API key or USDC micropayment.

    Priority:
    1. If VS_API_KEY is configured and provided key matches → allow.
    2. If tx_signature provided → verify USDC payment → allow if valid.
    3. If tool is in FREE_TIER_TOOLS and under daily limit → allow.
    4. Otherwise → return error dict with payment instructions.

    Returns None if authenticated, or an error dict if not.
    """
    required_amount = TOOL_PRICING.get(tool_name, 0.0)

    # 1. API key auth
    if api_key:
        configured_key = VS_API_KEY
        if configured_key and api_key == configured_key:
            return None
        if configured_key and api_key != configured_key:
            return {
                "error": "invalid_api_key",
                "message": "The provided API key is invalid.",
            }
        # api_key provided but VS_API_KEY not configured — fall through to payment

    # 2. Payment auth
    if tx_signature:
        result = await verify_solana_payment(tx_signature, expected_amount=required_amount)
        if result.get("verified"):
            return None
        return {
            "error": "payment_verification_failed",
            "message": result.get("error", "Payment verification failed."),
            "payment_instructions": get_payment_instructions(tool_name),
        }

    # 3. Free tier
    if tool_name in FREE_TIER_TOOLS:
        free_err = check_free_tier(tool_name, client_id)
        if free_err is None:
            return None
        return free_err

    # 4. No auth — return error with payment instructions
    return {
        "error": "authentication_required",
        "message": (
            f"Tool '{tool_name}' requires authentication. "
            "Provide an api_key or tx_signature (USDC payment on Solana)."
        ),
        "payment_instructions": get_payment_instructions(tool_name),
    }


def reset_free_tier_counts() -> None:
    """Reset free tier counters (for testing only)."""
    _free_tier_counts.clear()
