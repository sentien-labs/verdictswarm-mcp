import os

from .api_client import VerdictSwarmApiClient, VerdictSwarmClient


def main() -> None:
    from .server import mcp

    transport = os.getenv("VS_TRANSPORT", "stdio")
    # FastMCP reads host/port from HOST/PORT env vars for http transports
    mcp.run(transport=transport)


__all__ = ["main", "VerdictSwarmApiClient", "VerdictSwarmClient"]
