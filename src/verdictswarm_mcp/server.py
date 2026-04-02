from __future__ import annotations

import os
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .api_client import VerdictSwarmApiClient
from .config import TOOL_PRICING, USDC_MINT, VS_PAYMENT_WALLET
from .formatters import format_quick_score, format_report_markdown, format_risk_assessment
from .payments import verify_solana_payment

mcp = FastMCP(
    "VerdictSwarm",
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8000")),
)
api_client = VerdictSwarmApiClient()


@mcp.tool(
    annotations=ToolAnnotations(
        title="Full Token Scan",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def scan_token(
    token_address: Annotated[str, Field(description="Contract address of the token to scan")],
    chain: Annotated[str, Field(description="Blockchain network: solana, ethereum, base, etc.")] = "solana",
    depth: Annotated[str, Field(description="Scan depth: 'full' for all 6 agents, 'quick' for fast check")] = "full",
    api_key: Annotated[str, Field(description="API key for authentication (alternative to tx_signature)")] = "",
    tx_signature: Annotated[str, Field(description="Solana USDC payment transaction signature for pay-per-call auth")] = "",
) -> dict:
    """
    Run a full 6-agent VerdictSwarm risk scan.
    Returns consensus score, risk level, and agent-level findings for safe trading decisions.
    """
    return await api_client.scan(
        address=token_address,
        chain=chain,
        depth=depth,
        tier="PRO_PLUS",
        payment_signature=tx_signature,
    )


@mcp.tool(
    annotations=ToolAnnotations(
        title="Quick Score",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def get_quick_score(
    token_address: Annotated[str, Field(description="Contract address of the token to check")],
    chain: Annotated[str, Field(description="Blockchain network: solana, ethereum, base, etc.")] = "solana",
    api_key: Annotated[str, Field(description="API key for authentication (alternative to tx_signature)")] = "",
    tx_signature: Annotated[str, Field(description="Solana USDC payment transaction signature for pay-per-call auth")] = "",
    client_id: Annotated[str, Field(description="Client identifier for free-tier rate limiting")] = "anonymous",
) -> dict:
    """
    Fast cached token risk check.
    Returns score (0-100), risk band, and key token metadata for quick pre-trade screening.
    Free: 10 calls/day; paid calls: 0.02 USDC.
    """
    del api_key, client_id
    result = await api_client.quick_scan(
        address=token_address,
        chain=chain,
        payment_signature=tx_signature,
    )
    if "error" in result:
        return result
    return format_quick_score(result)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Rug Risk Check",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def check_rug_risk(
    token_address: Annotated[str, Field(description="Contract address of the token to check for rug-pull risk")],
    chain: Annotated[str, Field(description="Blockchain network: solana, ethereum, base, etc.")] = "solana",
    api_key: Annotated[str, Field(description="API key for authentication (alternative to tx_signature)")] = "",
    tx_signature: Annotated[str, Field(description="Solana USDC payment transaction signature for pay-per-call auth")] = "",
) -> dict:
    """
    Rug-pull-focused security scan.
    Checks mint/freeze controls, LP lock status, honeypot behavior, holder concentration, and returns SAFE/CAUTION/DANGER.
    """
    del api_key
    result = await api_client.rug_risk_scan(
        address=token_address,
        chain=chain,
        payment_signature=tx_signature,
    )
    if "error" in result:
        return result
    return format_risk_assessment(result)


# NOTE: Keeping function for backwards compatibility; not exposed as MCP tool until implementation is ready.
async def get_trending_risky(chain: str = "solana", min_risk_level: str = "HIGH", limit: int = 5) -> dict:
    """
    Deprecated placeholder: trending-risky discovery is not yet available.
    Returns a stable coming-soon response for compatibility.
    """
    return {
        "status": "coming_soon",
        "message": "Trending risky token discovery is not yet available in this API version.",
        "chain": chain,
        "min_risk_level": min_risk_level,
        "limit": max(1, min(20, int(limit))),
    }


@mcp.tool(
    annotations=ToolAnnotations(
        title="Token Report",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def get_token_report(
    token_address: Annotated[str, Field(description="Contract address of the token to generate a report for")],
    chain: Annotated[str, Field(description="Blockchain network: solana, ethereum, base, etc.")] = "solana",
    api_key: Annotated[str, Field(description="API key for authentication (alternative to tx_signature)")] = "",
    tx_signature: Annotated[str, Field(description="Solana USDC payment transaction signature for pay-per-call auth")] = "",
) -> str:
    """
    Generate a shareable markdown report for a token.
    Includes score, risk level, security findings, and recommendations.
    """
    del api_key
    result = await api_client.quick_scan(
        address=token_address,
        chain=chain,
        payment_signature=tx_signature,
    )
    if "error" in result:
        return f"# VerdictSwarm Token Report\n\nError: {result['error']}"
    return format_report_markdown(result)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Pricing Info",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def get_pricing(
    tool_name: Annotated[
        str | None,
        Field(description="Optional tool name to filter pricing for a specific tool only"),
    ] = None,
) -> dict:
    """
    Return current tool pricing and Solana payment details.
    Includes USDC rates, wallet/mint, free-tier limits, and transaction instructions.
    Optionally filter by tool name via the tool_name parameter.
    """
    selected_pricing = TOOL_PRICING
    if tool_name:
        requested_tool = tool_name.strip()
        if requested_tool:
            tool_cost = TOOL_PRICING.get(requested_tool)
            if tool_cost is None:
                return {
                    "pricing": {},
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
                    "error": f"Unknown tool_name '{requested_tool}'. "
                    f"Available tools: {', '.join(sorted(TOOL_PRICING.keys()))}",
                }

            selected_pricing = {requested_tool: tool_cost}

    return {
        "pricing": selected_pricing,
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


@mcp.tool(
    annotations=ToolAnnotations(
        title="Verify Payment",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def verify_payment(
    tx_signature: Annotated[str, Field(description="Solana transaction signature to verify")],
    tool_name: Annotated[str, Field(description="Name of the tool the payment is for (e.g. scan_token, get_quick_score)")],
) -> dict:
    """
    Verify a Solana USDC payment for a tool call.
    Returns verification status, sender, and required vs received amount.
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
