import os

from .api_client import VerdictSwarmApiClient, VerdictSwarmClient


def main() -> None:
    from .server import mcp

    transport = os.getenv("VS_TRANSPORT", "stdio")
    if transport == "streamable-http":
        host = os.getenv("VS_HOST", "0.0.0.0")
        port = int(os.getenv("VS_PORT", "8000"))
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        mcp.run()


__all__ = ["main", "VerdictSwarmApiClient", "VerdictSwarmClient"]
