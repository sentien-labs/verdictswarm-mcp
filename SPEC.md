# VerdictSwarm MCP Server — Implementation Spec

**Version:** 1.0
**Date:** 2026-02-17
**Status:** Building overnight, dev deploy by morning

---

## Overview

FastMCP server that exposes VerdictSwarm's 6-agent consensus token analysis to any MCP-compatible client (Claude Desktop, OpenClaw, Cursor, Codex, etc.). This makes VerdictSwarm the first crypto token scanner available via MCP.

## Architecture

```
MCP Client (Claude, OpenClaw, etc.)
        │
        │ MCP Protocol (stdio or streamable HTTP)
        ▼
┌─────────────────────────────────┐
│   VerdictSwarm MCP Server       │
│   (FastMCP + Python)            │
│                                 │
│   Tools:                        │
│   - scan_token                  │
│   - get_quick_score             │
│   - check_rug_risk              │
│   - get_trending_risky          │
│   - get_token_report            │
│                                 │
│   Resources:                    │
│   - verdictswarm://help         │
│                                 │
│   Prompts:                      │
│   - should_i_buy                │
│   - portfolio_check             │
│                                 │
│   Auth: API key via env var     │
│   Rate limit: Per-key tiers     │
└──────────────┬──────────────────┘
               │
               │ HTTP (httpx)
               ▼
┌─────────────────────────────────┐
│   VerdictSwarm API              │
│   (Existing Railway backend)    │
│   /api/v1/scan/{address}        │
│   /api/scan/stream              │
└─────────────────────────────────┘
```

## Design Decisions

### 1. Thin MCP wrapper over existing API
The MCP server does NOT embed the scan engine. It calls our existing Railway API via HTTP. This means:
- Single source of truth for scan logic
- MCP server is lightweight and stateless
- Can deploy MCP server anywhere (PyPI package, Railway, Cloudflare)
- API rate limiting and caching already work

### 2. Framework: FastMCP
- Decorator-based (`@mcp.tool()`)
- Auto-generates JSON schemas from type hints
- Docstrings become tool descriptions
- Minimal code, maximum discoverability

### 3. Auth via environment variable
Users set `VS_API_KEY` env var. Server passes it as bearer token to our API. No API key = free tier (10 calls/day, basic scores only).

### 4. Two transport modes
- **stdio** (default): For Claude Desktop, local MCP clients. Run via `uvx verdictswarm-mcp`
- **streamable-http** (future): For remote/hosted access at `mcp.verdictswarm.ai`

## Tools

### `scan_token`
Full 6-agent consensus scan. This is the premium tool.

```python
@mcp.tool()
async def scan_token(
    token_address: str,
    chain: str = "solana",
    depth: str = "full"
) -> dict:
    """
    Perform comprehensive token risk analysis using VerdictSwarm's 
    6-AI-agent consensus system.
    
    Analyzes: smart contract security, tokenomics, social sentiment, 
    technical indicators, macro conditions, and adversarial risk factors.
    
    Returns a verdict score (0-100), risk level, detailed findings from 
    each agent, and actionable recommendations.
    
    Args:
        token_address: The contract/mint address of the token
        chain: Blockchain - "solana", "ethereum", "base", or "bsc"
        depth: Analysis depth - "basic" (fast), "full" (all agents), 
               or "debate" (agents debate each other)
    
    Returns:
        Complete analysis with score, risk level, agent verdicts, 
        token metadata, and security findings
    """
```

### `get_quick_score`
Fast cached lookup. Free tier friendly.

```python
@mcp.tool()
async def get_quick_score(
    token_address: str,
    chain: str = "solana"
) -> dict:
    """
    Get a quick risk score for a token (uses cache when available).
    
    Returns the VerdictSwarm score (0-100), risk level, and basic 
    token metadata. Faster than full scan but may use cached data.
    
    Score interpretation:
    - 80-100: LOW risk (relatively safe)
    - 60-79: MEDIUM risk (proceed with caution)
    - 40-59: HIGH risk (significant concerns)
    - 0-39: CRITICAL risk (likely scam/rug)
    
    Args:
        token_address: The contract/mint address of the token
        chain: Blockchain - "solana", "ethereum", "base", or "bsc"
    """
```

### `check_rug_risk`
Focused security check — the most actionable tool for trading agents.

```python
@mcp.tool()
async def check_rug_risk(
    token_address: str,
    chain: str = "solana"
) -> dict:
    """
    Quick rug pull risk assessment for a token.
    
    Checks critical security indicators:
    - Mint authority (can dev print tokens?)
    - Freeze authority (can dev freeze wallets?)
    - LP burned/locked status
    - Honeypot detection (can you sell?)
    - Top holder concentration
    - Contract age
    - Bundle/sniper detection
    
    Returns a simple SAFE/CAUTION/DANGER verdict with specific 
    risk factors found.
    
    Args:
        token_address: The contract/mint address of the token  
        chain: Blockchain - "solana", "ethereum", "base", or "bsc"
    """
```

### `get_trending_risky`
Discovery tool — find tokens that need attention.

```python
@mcp.tool()
async def get_trending_risky(
    chain: str = "solana",
    min_risk_level: str = "HIGH",
    limit: int = 5
) -> dict:
    """
    Get trending tokens that have high risk scores.
    
    Useful for identifying potential scams gaining traction, or for 
    research into current market risks. Returns tokens sorted by 
    recent scan volume with their risk assessments.
    
    Args:
        chain: Blockchain to check - "solana", "ethereum", "base"
        min_risk_level: Minimum risk level to include - "MEDIUM", "HIGH", or "CRITICAL"
        limit: Number of tokens to return (1-20)
    """
```

### `get_token_report`
Formatted report for display/sharing.

```python
@mcp.tool()
async def get_token_report(
    token_address: str,
    chain: str = "solana"
) -> str:
    """
    Get a human-readable formatted report for a token.
    
    Returns a comprehensive markdown-formatted analysis report 
    suitable for sharing. Includes score, all agent verdicts, 
    security findings, and recommendations.
    
    Args:
        token_address: The contract/mint address of the token
        chain: Blockchain - "solana", "ethereum", "base", or "bsc"
    """
```

## Resources

### `verdictswarm://help`
Static resource describing available tools and scoring methodology.

### `verdictswarm://scoring`
Explanation of the 0-100 scoring system, agent weights, and grade meanings.

## Prompts

### `should_i_buy`
Pre-built prompt template for investment decisions.

```python
@mcp.prompt()
def should_i_buy(token_address: str, chain: str = "solana") -> str:
    """Analyze whether a token is worth buying."""
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
```

### `portfolio_check`
Pre-built prompt for portfolio risk assessment.

## File Structure

```
mcp-server/
├── SPEC.md                    # This file
├── pyproject.toml             # Package config (pip installable)
├── README.md                  # User-facing docs
├── src/
│   └── verdictswarm_mcp/
│       ├── __init__.py
│       ├── __main__.py        # Entry point: python -m verdictswarm_mcp
│       ├── server.py          # FastMCP server definition
│       ├── api_client.py      # HTTP client for VerdictSwarm API
│       ├── auth.py            # API key handling
│       ├── formatters.py      # Response formatting helpers
│       └── config.py          # Configuration (API URL, timeouts, etc.)
├── tests/
│   ├── conftest.py            # Shared fixtures, mock API responses
│   ├── test_server.py         # Tool integration tests
│   ├── test_api_client.py     # API client unit tests
│   ├── test_auth.py           # Auth/rate limit tests
│   ├── test_formatters.py     # Output formatting tests
│   └── test_prompts.py        # Prompt template tests
└── examples/
    ├── claude_desktop_config.json  # Example config for Claude Desktop
    └── basic_usage.py              # Example programmatic usage
```

## Dependencies

```toml
[project]
name = "verdictswarm-mcp"
version = "0.1.0"
description = "VerdictSwarm MCP Server - AI-powered crypto token risk analysis"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.scripts]
verdictswarm-mcp = "verdictswarm_mcp:main"
```

## API Client

The MCP server calls our existing API. Key endpoints:

| MCP Tool | API Endpoint | Method |
|----------|-------------|--------|
| `scan_token` | `/api/v1/scan` | POST |
| `get_quick_score` | `/api/v1/scan/{address}?chain={chain}` | GET |
| `check_rug_risk` | `/api/v1/scan/{address}?chain={chain}` | GET (parse security fields) |
| `get_token_report` | `/api/report/{address}` | GET |

For `check_rug_risk`, we extract security-specific fields from the scan response and format them as a focused risk assessment.

For `get_trending_risky`, this is a new capability — we'll query recent scans from cache/DB sorted by risk level. MVP can return "not yet available" and we'll add it in Phase 2.

## Configuration

```python
# config.py
import os

VS_API_URL = os.getenv("VS_API_URL", "https://verdictswarm-production.up.railway.app")
VS_API_KEY = os.getenv("VS_API_KEY", "")  # Empty = free tier
VS_TIMEOUT = int(os.getenv("VS_TIMEOUT", "120"))  # Scans can take time
```

## Test Strategy

### Unit Tests (mock API)
- Each tool returns correct structure
- Error handling (API down, invalid address, rate limited)
- Auth validation (missing key, expired key)
- Response formatting
- Edge cases (empty results, partial data)

### Integration Tests (real API, optional)
- End-to-end scan of known token (BONK on Solana)
- Verify score is in expected range
- Verify all fields present

### MCP Protocol Tests
- Server initializes correctly
- Tool discovery works
- Resource listing works
- Prompt listing works

## Deployment

### Phase 1: PyPI Package (MVP)
```bash
# Users install and run:
pip install verdictswarm-mcp
VS_API_KEY=vs_xxx verdictswarm-mcp

# Or with uvx (no install):
VS_API_KEY=vs_xxx uvx verdictswarm-mcp
```

### Phase 2: Hosted endpoint
```
https://mcp.verdictswarm.ai/mcp
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "verdictswarm": {
      "command": "uvx",
      "args": ["verdictswarm-mcp"],
      "env": {
        "VS_API_KEY": "vs_live_xxx"
      }
    }
  }
}
```

## Success Criteria
- [ ] All 5 tools functional and tested
- [ ] 20+ tests passing
- [ ] Works with Claude Desktop locally
- [ ] README with clear setup instructions
- [ ] Published to PyPI (or ready to publish)
- [ ] Listed on MCP Registry / PulseMCP
