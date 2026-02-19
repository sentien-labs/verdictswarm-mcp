import os

VS_API_URL = os.getenv("VS_API_URL", "https://verdictswarm-production.up.railway.app")
VS_API_KEY = os.getenv("VS_API_KEY", "")
VS_TIMEOUT = int(os.getenv("VS_TIMEOUT", "120"))

# Payment configuration
VS_PAYMENT_WALLET = os.getenv("VS_PAYMENT_WALLET", "")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# USDC SPL token mint on Solana mainnet
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Per-tool pricing in USDC (USD equivalent)
TOOL_PRICING: dict[str, float] = {
    "scan_token": 0.10,
    "get_quick_score": 0.02,
    "check_rug_risk": 0.05,
    "analyze_contract": 0.10,
    "compare_tokens": 0.15,
    # Tools below are free
    "get_trending_risky": 0.0,
    "get_token_report": 0.02,
    "get_pricing": 0.0,
    "verify_payment": 0.0,
}

# Free tier: calls per day for get_quick_score only
FREE_TIER_DAILY_LIMIT = 10
