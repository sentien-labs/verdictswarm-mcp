from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .api_client import VerdictSwarmApiClient
from .auth import authenticate
from .config import TOOL_PRICING, USDC_MINT, VS_PAYMENT_WALLET
from .formatters import format_quick_score, format_report_markdown, format_risk_assessment
from .payments import get_payment_instructions, verify_solana_payment

mcp = FastMCP("VerdictSwarm")
api_client = VerdictSwarmApiClient()


@mcp.tool()
async def scan_token(
    token_address: str,
    chain: str = "solana",
    depth: str = "full",
    api_key: str = "",
    tx_signature: str = "",
) -> dict:
    """
    Perform comprehensive token risk analysis using VerdictSwarm's 6-AI-agent consensus system.

    This tool executes a full scan of a token contract and returns detailed findings
    including overall score, risk level, agent-level analysis, and security checks.

    Cost: 0.10 USDC per call (or valid API key).

    Args:
        token_address: The contract or mint address to analyze.
        chain: Target blockchain (solana, ethereum, base, bsc).
        depth: Analysis depth (basic, full, debate).
        api_key: Optional API key for authenticated access.
        tx_signature: Optional Solana transaction signature for USDC micropayment.

    Returns:
        Dictionary containing full analysis results from VerdictSwarm API, or an error payload.
    """
    auth_err = await authenticate(
        "scan_token",
        api_key=api_key or None,
        tx_signature=tx_signature or None,
    )
    if auth_err:
        return auth_err
    return await api_client.scan(address=token_address, chain=chain, depth=depth, tier="standard")


@mcp.tool()
async def get_quick_score(
    token_address: str,
    chain: str = "solana",
    api_key: str = "",
    tx_signature: str = "",
    client_id: str = "anonymous",
) -> dict:
    """
    Get a quick risk score for a token using cached or fast-path analysis.

    Use this when you need a fast confidence check before deeper analysis.
    Returns score (0-100), derived risk level, and basic token metadata.

    Free tier: 10 calls/day (no auth required).
    Cost: 0.02 USDC per call beyond free tier.

    Args:
        token_address: The contract or mint address to inspect.
        chain: Target blockchain (solana, ethereum, base, bsc).
        api_key: Optional API key for authenticated access.
        tx_signature: Optional Solana transaction signature for USDC micropayment.
        client_id: Optional identifier for free-tier rate limiting (e.g. agent wallet address).

    Returns:
        Minimal structured score summary, or an error payload.
    """
    auth_err = await authenticate(
        "get_quick_score",
        api_key=api_key or None,
        tx_signature=tx_signature or None,
        client_id=client_id or "anonymous",
    )
    if auth_err:
        return auth_err
    result = await api_client.quick_scan(address=token_address, chain=chain)
    if "error" in result:
        return result
    return format_quick_score(result)


@mcp.tool()
async def check_rug_risk(
    token_address: str,
    chain: str = "solana",
    api_key: str = "",
    tx_signature: str = "",
) -> dict:
    """
    Run a focused rug-pull risk assessment with high-signal security indicators.

    Evaluates common red flags such as mint/freeze controls, liquidity lock/burn status,
    honeypot-like behavior, concentration concerns, and related risk indicators present in
    the scan response.

    Cost: 0.05 USDC per call (or valid API key).

    Args:
        token_address: The contract or mint address to assess.
        chain: Target blockchain (solana, ethereum, base, bsc).
        api_key: Optional API key for authenticated access.
        tx_signature: Optional Solana transaction signature for USDC micropayment.

    Returns:
        Structured verdict containing SAFE/CAUTION/DANGER, risk factors, and security checks,
        or an error payload.
    """
    auth_err = await authenticate(
        "check_rug_risk",
        api_key=api_key or None,
        tx_signature=tx_signature or None,
    )
    if auth_err:
        return auth_err
    result = await api_client.quick_scan(address=token_address, chain=chain)
    if "error" in result:
        return result
    return format_risk_assessment(result)


@mcp.tool()
async def get_trending_risky(chain: str = "solana", min_risk_level: str = "HIGH", limit: int = 5) -> dict:
    """
    Get trending risky tokens for the selected chain.

    This endpoint is planned for a future API phase. For now, it returns a clear placeholder
    payload so clients can integrate against a stable tool signature.

    Args:
        chain: Blockchain to query (solana, ethereum, base).
        min_risk_level: Threshold to include (MEDIUM, HIGH, CRITICAL).
        limit: Number of items requested (1-20).

    Returns:
        Placeholder response describing current availability status.
    """
    return {
        "status": "coming_soon",
        "message": "Trending risky token discovery is not yet available in this API version.",
        "chain": chain,
        "min_risk_level": min_risk_level,
        "limit": max(1, min(20, int(limit))),
    }


@mcp.tool()
async def get_token_report(
    token_address: str,
    chain: str = "solana",
    api_key: str = "",
    tx_signature: str = "",
) -> str:
    """
    Get a human-readable markdown report for a token.

    Generates a formatted report suitable for sharing that includes score, risk level,
    major risk factors, security checks, and optional recommendation fields when available.

    Cost: 0.02 USDC per call (or valid API key).

    Args:
        token_address: The contract or mint address to report on.
        chain: Target blockchain (solana, ethereum, base, bsc).
        api_key: Optional API key for authenticated access.
        tx_signature: Optional Solana transaction signature for USDC micropayment.

    Returns:
        Markdown-formatted report text, or a markdown error message.
    """
    auth_err = await authenticate(
        "get_token_report",
        api_key=api_key or None,
        tx_signature=tx_signature or None,
    )
    if auth_err:
        return (
            f"# VerdictSwarm Token Report\n\n"
            f"**Authentication required.**\n\n"
            f"Error: {auth_err.get('message', 'Authentication failed.')}\n\n"
            f"Payment: {auth_err.get('payment_instructions', {})}"
        )
    result = await api_client.quick_scan(address=token_address, chain=chain)
    if "error" in result:
        return f"# VerdictSwarm Token Report\n\nError: {result['error']}"
    return format_report_markdown(result)


@mcp.tool()
async def get_pricing() -> dict:
    """
    Get the current pricing table for all VerdictSwarm MCP tools.

    Returns pricing in USDC per call, payment wallet address, USDC mint,
    and instructions for submitting micropayments from autonomous agents.

    Returns:
        Dictionary with per-tool pricing, wallet info, and payment instructions.
    """
    return {
        "pricing": TOOL_PRICING,
        "currency": "USDC",
        "network": "solana-mainnet",
        "usdc_mint": USDC_MINT,
        "payment_wallet": VS_PAYMENT_WALLET,
        "free_tier": {
            "tool": "get_quick_score",
            "daily_limit": 10,
            "requires_client_id": True,
        },
        "instructions": (
            "Send USDC on Solana to the payment_wallet. "
            "Pass the transaction signature as tx_signature when calling the tool. "
            "Each signature can only be used once (replay protection)."
        ),
    }


@mcp.tool()
async def verify_payment(tx_signature: str, tool_name: str) -> dict:
    """
    Verify that a Solana USDC payment was received for a specific tool call.

    Agents can use this to confirm their payment before calling an expensive tool,
    or to debug failed payment verifications.

    Args:
        tx_signature: The Solana transaction signature of the USDC transfer.
        tool_name: The tool name the payment is intended for (used to check amount).

    Returns:
        Verification result with verified status, amount, and sender info.
    """
    required_amount = TOOL_PRICING.get(tool_name, 0.0)
    result = await verify_solana_payment(tx_signature, expected_amount=required_amount)
    result["tool"] = tool_name
    result["required_amount_usdc"] = required_amount
    return result


@mcp.resource("verdictswarm://help")
def help_resource() -> str:
    return (
        "VerdictSwarm MCP provides AI-driven token risk analysis tools:\n"
        "- scan_token: Full consensus scan (0.10 USDC)\n"
        "- get_quick_score: Fast score lookup (free tier: 10/day, then 0.02 USDC)\n"
        "- check_rug_risk: Focused security verdict (0.05 USDC)\n"
        "- get_trending_risky: Trending risky tokens (coming soon, free)\n"
        "- get_token_report: Shareable markdown report (0.02 USDC)\n"
        "- get_pricing: View pricing table (free)\n"
        "- verify_payment: Verify your USDC payment (free)\n"
        "\n"
        "Auth: provide api_key OR tx_signature (Solana USDC payment).\n"
        "Tip: call get_pricing first to see wallet address and amounts."
    )


@mcp.resource("verdictswarm://scoring")
def scoring_resource() -> str:
    return (
        "VerdictSwarm scoring guide (0-100):\n"
        "- 80-100: LOW risk (Grade A)\n"
        "- 70-79:  LOW-MEDIUM (Grade B)\n"
        "- 60-69:  MEDIUM (Grade C)\n"
        "- 40-59:  HIGH (Grade D)\n"
        "- 0-39:   CRITICAL (Grade F)\n"
        "\n"
        "Always combine score with security checks and market context."
    )


@mcp.prompt()
def should_i_buy(token_address: str, chain: str = "solana") -> str:
    return f"""Please analyze this token for investment potential:

Token: {token_address} on {chain}

Steps:
1. Use scan_token to get the full analysis
2. Use check_rug_risk to verify security
3. Based on the results, provide:
   - Overall recommendation (BUY / HOLD / AVOID)
   - Key risk factors
   - What to watch for
   - Suggested position size relative to risk

Be direct and honest about risks. If this looks like a scam, say so clearly."""


@mcp.prompt()
def portfolio_check(tokens: str, chain: str = "solana") -> str:
    return f"""Review this portfolio for downside risk and rug exposure.

Chain: {chain}
Tokens (comma-separated addresses): {tokens}

For each token:
1. Run get_quick_score
2. Run check_rug_risk
3. Classify as KEEP / REDUCE / EXIT

Then provide:
- Portfolio-level risk summary
- Concentration concerns
- Priority actions for risk reduction
- A safer allocation suggestion
"""
