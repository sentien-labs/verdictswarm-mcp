FROM python:3.12-slim

WORKDIR /app

# Install the package from PyPI
RUN pip install --no-cache-dir verdictswarm-mcp>=0.1.5

# Run as streamable-http for remote hosting (Smithery, Glama, etc.)
ENV VS_TRANSPORT=streamable-http
ENV VS_HOST=0.0.0.0
ENV VS_PORT=8000
ENV VS_API_URL=https://api.vswarm.io

EXPOSE 8000

ENTRYPOINT ["verdictswarm-mcp"]
