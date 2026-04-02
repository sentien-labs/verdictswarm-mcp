FROM python:3.12-slim

WORKDIR /app

# v0.1.6 — streamable-http transport for remote MCP hosting
COPY pyproject.toml README.md LICENSE ./
COPY src/ src/
RUN pip install --no-cache-dir .

# Run as streamable-http for remote hosting (Smithery, Glama, etc.)
ENV VS_TRANSPORT=streamable-http
ENV VS_HOST=0.0.0.0
ENV VS_PORT=8000
ENV VS_API_URL=https://api.vswarm.io

EXPOSE 8000

ENTRYPOINT ["verdictswarm-mcp"]
