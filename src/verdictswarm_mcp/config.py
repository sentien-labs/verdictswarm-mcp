import os

VS_API_URL = os.getenv("VS_API_URL", "https://api.vswarm.io")
VS_API_KEY = os.getenv("VS_API_KEY", "")
VS_MCP_SERVICE_KEY = os.getenv("VS_MCP_SERVICE_KEY", "")
VS_TIMEOUT = int(os.getenv("VS_TIMEOUT", "120"))

# Payment configuration
VS_PAYMENT_WALLET = os.getenv("VS_PAYMENT_WALLET", "")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# USDC SPL token mint on Solana mainnet
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Per-tool pricing in USDC (USD equivalent)
# Approved pricing per PRODUCT_SPEC.md (2026-02-19)
TOOL_PRICING: dict[str, float] = {
    "scan_token": 1.00,        # Full 6-agent scan — 80% margin
    "get_quick_score": 0.10,   # Cached score — 90% margin
    "check_rug_risk": 0.50,    # Security-focused — 60% margin
    "get_token_report": 0.10,  # Formatted report — 90% margin
    # Free tools
    "get_trending_risky": 0.0,
    "get_pricing": 0.0,
    "verify_payment": 0.0,
}

# Free tier: 10 scans per wallet (lifetime, not daily)
FREE_TIER_LIFETIME_LIMIT = 10
