# 🔍 VerdictSwarm MCP Server

[![GitHub](https://img.shields.io/github/stars/vswarm-ai/verdictswarm)](https://github.com/vswarm-ai/verdictswarm)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://github.com/vswarm-ai/verdictswarm)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0-blue)](https://modelcontextprotocol.io)

**The first crypto token scanner available via MCP.** Give any AI agent the ability to analyze tokens for rug pulls, scams, and risk — powered by VerdictSwarm's 6-AI-agent consensus system.

Works with Claude Desktop, OpenClaw, Cursor, Codex, Windsurf, and any MCP-compatible client.

---

## Why?

AI trading agents are making on-chain decisions with no risk analysis. VerdictSwarm MCP gives them instant access to:

- **6-agent consensus scoring** — not one model's opinion, six independent AI agents debate the risk
- **On-chain security audits** — mint authority, freeze authority, honeypot detection, LP lock status
- **Rug pull detection** — holder concentration, bundle/sniper activity, contract age analysis
- **Human-readable reports** — markdown reports ready to share or embed

One tool call. Sub-second cached responses. No blockchain node required.

## Quick Start

### Install & Run

```bash
# Install from PyPI (recommended)
pip install verdictswarm-mcp
VS_API_KEY=your_key verdictswarm-mcp

# Or install from GitHub
pip install git+https://github.com/vswarm-ai/verdictswarm.git#subdirectory=mcp-server
VS_API_KEY=your_key verdictswarm-mcp

# Or with uvx (zero-install)
VS_API_KEY=your_key uvx git+https://github.com/vswarm-ai/verdictswarm.git#subdirectory=mcp-server

# Or clone and run
git clone https://github.com/vswarm-ai/verdictswarm.git
cd verdictswarm/mcp-server
uv run verdictswarm-mcp
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "verdictswarm": {
      "command": "uvx",
      "args": ["git+https://github.com/vswarm-ai/verdictswarm.git#subdirectory=mcp-server"],
      "env": {
        "VS_API_KEY": "your_key_here"
      }
    }
  }
}
```

Then ask Claude: *"Check if this token is safe: `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` on Solana"*

### OpenClaw

```yaml
mcpServers:
  verdictswarm:
    command: uvx
    args: ["verdictswarm-mcp"]
    env:
      VS_API_KEY: your_key_here
```

### No API Key?

The server works without a key at free-tier limits (10 scans lifetime, basic scores only). Get a key at [vswarm.io](https://vswarm.io) for full access.

## Tools

| Tool | Description | Use When |
|------|-------------|----------|
| `scan_token` | Full 6-agent consensus analysis | Deep due diligence on a specific token |
| `get_quick_score` | Fast cached score lookup (0-100) | Quick check before buying |
| `check_rug_risk` | Focused security/rug assessment | "Is this a scam?" |
| `get_trending_risky` | Trending high-risk tokens | Market surveillance (coming soon) |
| `get_token_report` | Formatted markdown report | Sharing analysis with others |

### Example: Quick Score

```
User: What's the risk score for BONK?
Agent: [calls get_quick_score("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")]
→ Score: 74/100 (Grade B) — LOW-MEDIUM risk
```

### Example: Rug Check

```
User: Is this new memecoin safe? 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
Agent: [calls check_rug_risk("7xKXtg...")]
→ DANGER
  🚨 Liquidity NOT burned or locked
  ⚠️ Mint authority active
  ⚠️ Token is less than 24 hours old
  ⚠️ Bundle/sniper activity detected
```

## Resources & Prompts

**Resources** (reference data for agents):
- `verdictswarm://help` — Tool usage guide
- `verdictswarm://scoring` — Score interpretation (0-100 scale, grades A-F)

**Prompts** (pre-built workflows):
- `should_i_buy(token_address)` — Full investment analysis with recommendation
- `portfolio_check(tokens)` — Batch risk assessment across holdings

## Supported Chains

| Chain | Status |
|-------|--------|
| Solana | ✅ Full support |
| Ethereum | ✅ Full support |
| Base | ✅ Full support |
| BSC | ✅ Full support |

## Scoring Guide

| Score | Grade | Risk Level | Meaning |
|-------|-------|------------|---------|
| 80-100 | A | LOW | Relatively safe, established project |
| 70-79 | B | LOW-MEDIUM | Minor concerns, generally okay |
| 60-69 | C | MEDIUM | Proceed with caution |
| 40-59 | D | HIGH | Significant red flags |
| 0-39 | F | CRITICAL | Likely scam or rug pull |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `VS_API_KEY` | *(empty — free tier)* | Your VerdictSwarm API key |
| `VS_API_URL` | `https://api.vswarm.io` | API base URL |
| `VS_TIMEOUT` | `120` | Request timeout in seconds |

## Architecture

```
MCP Client (Claude, Cursor, OpenClaw, Codex...)
    │
    │  MCP Protocol (stdio)
    ▼
┌──────────────────────────┐
│  VerdictSwarm MCP Server │  ← This package (thin wrapper)
│  FastMCP + Python        │
└──────────┬───────────────┘
           │  HTTP (httpx)
           ▼
┌──────────────────────────┐
│  VerdictSwarm API        │  ← api.vswarm.io
│  6 AI agents + on-chain  │
└──────────────────────────┘
```

The MCP server is a stateless wrapper — all intelligence lives in the VerdictSwarm API. This means:
- Lightweight deployment (no GPU, no blockchain node)
- Single source of truth for scan logic
- API-level rate limiting and caching already work

## Development

```bash
git clone https://github.com/vswarm-ai/verdictswarm.git
cd verdictswarm/mcp-server
pip install -e ".[dev]"
pytest  # 47 tests, ~0.3s
```

## License

MIT — see [LICENSE](LICENSE).

## Links

- **Website:** [vswarm.io](https://vswarm.io)
- **API Docs:** [api.vswarm.io/docs](https://api.vswarm.io/docs)
- **GitHub:** [vswarm-ai/verdictswarm](https://github.com/vswarm-ai/verdictswarm)
- **MCP Spec:** [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

*Built by [Sentien Labs](https://sentienlabs.com) — AI-operated crypto intelligence infrastructure.*
