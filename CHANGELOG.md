# Changelog

## [0.1.0] - 2026-02-18

### Added
- Initial release — first crypto token scanner available via MCP
- 5 tools: `scan_token`, `get_quick_score`, `check_rug_risk`, `get_trending_risky`, `get_token_report`
- 2 resources: `verdictswarm://help`, `verdictswarm://scoring`
- 2 prompts: `should_i_buy`, `portfolio_check`
- Async HTTP client with full error handling (timeouts, rate limits, auth failures)
- Security-focused rug risk formatter with on-chain indicator checks
- Score-to-grade (A-F) normalization from 0-10 and 0-100 API scales
- API key auth via `VS_API_KEY` environment variable (empty = free tier)
- stdio transport for Claude Desktop, OpenClaw, Cursor, and other local MCP clients
- 47 unit tests with full coverage of tools, formatters, client, config, and prompts
- MIT license
