"""Basic programmatic usage example for VerdictSwarm MCP internals."""

import asyncio

from verdictswarm_mcp.api_client import VerdictSwarmApiClient
from verdictswarm_mcp.formatters import format_quick_score, format_report_markdown, format_risk_assessment


async def main() -> None:
    client = VerdictSwarmApiClient()

    token_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"  # Example
    chain = "solana"

    quick = await client.quick_scan(token_address, chain)
    if "error" in quick:
        print("Quick scan error:", quick["error"])
        return

    print("Quick Score:")
    print(format_quick_score(quick))
    print()

    print("Rug Risk Assessment:")
    print(format_risk_assessment(quick))
    print()

    print("Markdown Report:")
    print(format_report_markdown(quick))


if __name__ == "__main__":
    asyncio.run(main())
