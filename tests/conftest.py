import pytest


@pytest.fixture
def mock_scan_result():
    return {
        "data": {
            "address": "So11111111111111111111111111111111111111112",
            "chain": "solana",
            "depth": "full",
            "tier": "standard",
            "score": 6.7,
            "risk_level": "MEDIUM",
            "flags": ["new_token", "moderate_concentration"],
            "bots": {
                "sentinel": {
                    "score": 68,
                    "sentiment": "neutral",
                    "reasoning": "No immediate critical exploit pattern, but watch concentration and age.",
                },
                "anomaly": {
                    "score": 64,
                    "sentiment": "cautious",
                    "reasoning": "Behavior appears normal for early-stage token with moderate risk markers.",
                },
            },
            "token": {
                "name": "Sample Token",
                "symbol": "SMPL",
                "price_usd": 0.123456,
                "mcap": 1250000,
                "volume_24h": 250000,
                "liquidity_usd": 300000,
                "contract_age_days": 30,
                "holder_count": 5000,
                "top10_holders_pct": 35,
                "mint_authority": None,
                "freeze_authority": None,
                "lp_burned_or_locked": True,
                "bundle_detected": False,
                "goplus_trusted": True,
                "is_honeypot": False,
            },
            "holder_quality": {
                "score": 73,
                "grade": "B",
            },
            "scanned_at": "2026-02-17T23:00:00Z",
        }
    }


@pytest.fixture
def mock_dangerous_result(mock_scan_result):
    result = mock_scan_result.copy()
    result["data"] = {**mock_scan_result["data"]}
    result["data"]["score"] = 2.5
    result["data"]["risk_level"] = "CRITICAL"
    result["data"]["flags"] = ["honeypot", "lp_unlocked", "fresh_contract"]
    result["data"]["token"] = {
        **mock_scan_result["data"]["token"],
        "mint_authority": "SomeAuthority",
        "freeze_authority": "SomeAuth",
        "lp_burned_or_locked": False,
        "top10_holders_pct": 85,
        "bundle_detected": True,
        "contract_age_days": 0,
        "is_honeypot": True,
    }
    return result


@pytest.fixture
def mock_free_result():
    return {
        "data": {
            "address": "FreeTier111111111111111111111111111111111111",
            "chain": "solana",
            "depth": "basic",
            "tier": "free",
            "risk_level": "MEDIUM",
            "flags": ["limited_analysis"],
            "free_tier_result": {
                "confidence": 0.67,
                "summary": "Moderate risk indicators in free tier scan.",
            },
            "locked_bots": ["whale_guard", "meme_hunter", "liquidity_ai"],
            "bots": {
                "free_guard": {
                    "score": 67,
                    "sentiment": "neutral",
                    "reasoning": "Core checks complete; premium bot insights locked.",
                }
            },
            "token": {
                "name": "Free Token",
                "symbol": "FREE",
                "price_usd": 0.0025,
                "mcap": 500000,
                "volume_24h": 45000,
                "liquidity_usd": 90000,
                "contract_age_days": 12,
                "holder_count": 2100,
                "top10_holders_pct": 41,
                "mint_authority": None,
                "freeze_authority": None,
                "lp_burned_or_locked": True,
                "bundle_detected": False,
                "goplus_trusted": True,
                "is_honeypot": False,
            },
            "holder_quality": {
                "score": 66,
                "grade": "C",
            },
            "scanned_at": "2026-02-17T23:10:00Z",
        }
    }
