FROM python:3.12-slim

WORKDIR /app

# v0.1.6 — streamable-http transport for remote MCP hosting
COPY pyproject.toml README.md LICENSE ./
COPY src/ src/
RUN pip install --no-cache-dir .

# FastMCP reads HOST/PORT env vars for streamable-http transport
ENV VS_TRANSPORT=streamable-http
ENV HOST=0.0.0.0
ENV PORT=8000
ENV VS_API_URL=https://api.vswarm.io

EXPOSE 8000

ENTRYPOINT ["verdictswarm-mcp"]
