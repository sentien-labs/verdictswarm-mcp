FROM python:3.12-slim

WORKDIR /app

# v0.1.6 — streamable-http transport for remote MCP hosting
COPY pyproject.toml README.md LICENSE ./
COPY src/ src/
RUN pip install --no-cache-dir .

ENV VS_TRANSPORT=streamable-http
ENV VS_API_URL=https://api.vswarm.io

EXPOSE 8000

# Run uvicorn directly with explicit 0.0.0.0 binding
CMD ["python", "-c", "from verdictswarm_mcp.server import mcp; import uvicorn; uvicorn.run(mcp.streamable_http_app(), host='0.0.0.0', port=8000)"]
