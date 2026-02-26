FROM python:3.12-slim

WORKDIR /app

# Install the package from PyPI
RUN pip install --no-cache-dir verdictswarm-mcp==0.1.0

# MCP server runs via stdio (standard MCP transport)
# Environment variables required at runtime:
# VERDICTSWARM_API_URL - API base URL (default: https://verdictswarm-production.up.railway.app)
ENV VERDICTSWARM_API_URL=https://verdictswarm-production.up.railway.app

ENTRYPOINT ["verdictswarm-mcp"]

