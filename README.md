# 🔍 VerdictSwarm MCP Server

[![GitHub](https://img.shields.io/github/stars/sentien-labs/verdictswarm-mcp)](https://github.com/sentien-labs/verdictswarm-mcp)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://github.com/sentien-labs/verdictswarm-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0-blue)](https://modelcontextprotocol.io)
[![sentien-labs/verdictswarm-mcp MCP server](https://glama.ai/mcp/servers/sentien-labs/verdictswarm-mcp/badge)](https://glama.ai/mcp/servers/sentien-labs/verdictswarm-mcp)
[![Awesome MCP Servers](https://img.shields.io/badge/Awesome-MCP%20Servers-fc60a8?logo=awesomelists)](https://github.com/punkpeye/awesome-mcp-servers)
[![PyPI](https://img.shields.io/pypi/v/verdictswarm-mcp)](https://pypi.org/project/verdictswarm-mcp/)
[![Smithery](https://smithery.ai/badge/sentien-labs/verdictswarm-mcp)](https://smithery.ai/servers/sentien-labs/verdictswarm-mcp)

**Fight AI with AI.** Scammers build rugs with AI. Your agent catches them with 6.

The security layer for AI agents that touch money. One tool call between your trading agent and a rug pull.

Works with Claude Desktop, OpenClaw, Cursor, Codex, Windsurf, and any MCP-compatible client.

---

## Why?

AI trading agents are making autonomous on-chain decisions with little or no risk review. Scammers are building rugs that bypass many single-algorithm scanners. The agent attack surface is now direct and financial, and bad results are costly.

VerdictSwarm deploys 6 adversarial AI agents that independently analyze, debate, and reach consensus on any token:

- **Adversarial debate** - not one model's opinion. Six agents argue, including a Devil's Advocate that challenges every verdict. You see dissenting opinions.
- **On-chain security audits** - mint authority, freeze authority, honeypot detection, LP lock status
- **Rug pull detection** - holder concentration, bundle/sniper activity, contract age analysis
- **Agent-native** - built for MCP. One tool call. Sub-second cached responses. No blockchain node required.

## How It's Different

|  | VerdictSwarm | Single-Score Scanners |
|---|---|---|
| **Method** | 6 AI agents debate adversarially | One algorithm, one number |
| **Transparency** | See dissenting opinions + reasoning | Black box trust score |
| **Devil's Advocate** | Dedicated agent challenges every verdict | No contrarian analysis |
| **Coverage** | On-chain + social + contract + holder analysis | Usually 1-2 signals |
| **Agent-native** | MCP protocol, one tool call | REST API, manual integration |

> Most scanners give you a number. VerdictSwarm gives you the argument.

## Quick Start

### Install & Run

```bash
# Install from PyPI (recommended)
pip install verdictswarm-mcp

# Run with uvx (zero-install)
VS_API_KEY=your_key_here uvx verdictswarm-mcp
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "verdictswarm": {
      "command": "uvx",
      "args": ["verdictswarm-mcp"],
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

### Cursor

Uses `claude_desktop_config.json` format.

```json
{
  "mcpServers": {
    "verdictswarm": {
      "command": "uvx",
      "args": ["verdictswarm-mcp"],
      "env": {
        "VS_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Windsurf

```json
{
  "mcpServers": {
    "verdictswarm": {
      "command": "uvx",
      "args": ["verdictswarm-mcp"],
      "env": {
        "VS_API_KEY": "your_key_here"
      }
    }
  }
}
```

### VS Code + Cline

```json
{
  "cline.mcpServers": {
    "verdictswarm": {
      "command": "uvx",
      "args": ["verdictswarm-mcp"],
      "env": {
        "VS_API_KEY": "your_key_here"
      }
    }
  }
}
```

### No API Key?

You get 10 free full 6-agent scans, no credit card required.

## Tools

| Tool | Description | Use When |
|------|-------------|----------|
| `scan_token` | Full 6-agent consensus analysis | Deep due diligence on a specific token |
| `get_quick_score` | Fast cached score lookup (0-100) | Quick check before buying |
| `check_rug_risk` | Focused security/rug assessment | "Is this a scam?" |
| `get_token_report` | Formatted markdown report | Sharing analysis with others |
| `get_pricing` | Tool pricing and payment details | View costs and Solana payment info |
| `verify_payment` | Verify USDC payment on Solana | Confirm payment before calling paid tools |

## Real Results

> Is $CRABGE safe?
>
> VerdictSwarm Score: 23/100 (Grade F - CRITICAL RISK)
>
> 🔴 Security Agent: Mint authority still active. Deployer can mint unlimited tokens.
> 🔴 Liquidity Agent: Only $2,400 liquidity. 89% held by top 5 wallets.
> 🟡 Social Agent: 340 holders but suspicious clustering pattern.
> 🔴 Devil's Advocate: "Even the bull case here is terrible. Contract is 6 hours old with active mint authority."
>
> Verdict: AVOID - High probability rug pull

### Example: Quick Score

```
User: What's the risk score for BONK?
Agent: [calls get_quick_score("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")]
→ Score: 74/100 (Grade B) - LOW-MEDIUM risk
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
- `verdictswarm://help` - Tool usage guide
- `verdictswarm://scoring` - Score interpretation (0-100 scale, grades A-F)

**Prompts** (pre-built workflows):
- `should_i_buy(token_address)` - Full investment analysis with recommendation
- `portfolio_check(tokens)` - Batch risk assessment across holdings

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
| `VS_API_KEY` | *(empty - free tier)* | Your VerdictSwarm API key |
| `VS_API_URL` | `https://api.vswarm.io` | API base URL |
| `VS_TIMEOUT` | `120` | Request timeout in seconds |

## Architecture

```
MCP Client (Claude, Cursor, OpenClaw, Codex...)
    |
    |  MCP Protocol (stdio)
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

The MCP server is a stateless wrapper. All intelligence lives in the VerdictSwarm API. This means:
- Lightweight deployment (no GPU, no blockchain node)
- Single source of truth for scan logic
- API-level rate limiting and caching already work

## Development

```bash
git clone https://github.com/sentien-labs/verdictswarm-mcp.git
cd verdictswarm-mcp
pip install -e ".[dev]"
pytest  # 47 tests, ~0.3s
```

## License

MIT - see [LICENSE](LICENSE).

## Links

- **Website:** [vswarm.io](https://vswarm.io)
- **API Docs:** [api.vswarm.io/docs](https://api.vswarm.io/docs)
- **GitHub:** [sentien-labs/verdictswarm-mcp](https://github.com/sentien-labs/verdictswarm-mcp)
- **MCP Spec:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Smithery:** [smithery.ai/servers/sentien-labs/verdictswarm-mcp](https://smithery.ai/servers/sentien-labs/verdictswarm-mcp)
- **awesome-mcp-servers:** [Listed here](https://github.com/punkpeye/awesome-mcp-servers)

---

*Built by [Sentien Labs](https://sentienlabs.com) - AI-operated crypto intelligence infrastructure.*