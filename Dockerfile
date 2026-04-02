FROM python:3.12-slim

WORKDIR /app

# Copy source and install from local (includes streamable-http transport)
COPY . .
RUN pip install --no-cache-dir .

# Run as streamable-http for remote hosting (Smithery, Glama, etc.)
ENV VS_TRANSPORT=streamable-http
ENV VS_HOST=0.0.0.0
ENV VS_PORT=8000
ENV VS_API_URL=https://api.vswarm.io

EXPOSE 8000

ENTRYPOINT ["verdictswarm-mcp"]
