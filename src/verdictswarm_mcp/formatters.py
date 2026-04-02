"""Response formatting helpers for VerdictSwarm MCP Server.

Transforms raw API scan results into focused, actionable outputs
for different MCP tool use cases.
"""
from __future__ import annotations

from typing import Any


def score_to_grade(score: float | int | None) -> str:
    """Convert a 0-100 score to a letter grade."""
    if score is None:
        return "N/A"
    value = float(score)
    if value >= 80:
        return "A"
    if value >= 70:
        return "B"
    if value >= 60:
        return "C"
    if value >= 40:
        return "D"
    return "F"


def _unwrap_data(result: dict[str, Any]) -> dict[str, Any]:
    """Our API wraps responses in {"data": {...}}. Unwrap if needed."""
    if "data" in result and isinstance(result["data"], dict):
        return result["data"]
    return result


def _get_score_100(data: dict[str, Any]) -> float | None:
    """Extract score and normalize to 0-100 scale.
    
    Our API returns score on 0-10 scale. Multiply by 10 for display.
    If score is already > 10, assume it's already 0-100.
    """
    score = data.get("score")
    if score is None:
        # Free tier returns verdict + confidence, NOT a numeric score.
        # Don't use confidence as score — it measures certainty, not quality.
        return None
    score = float(score)
    if score <= 10:
        return score * 10
    return score


def _get_token(data: dict[str, Any]) -> dict[str, Any]:
    """Extract token metadata from scan result."""
    return data.get("token", {})


def _get_risk_level(data: dict[str, Any], score_100: float | None) -> str:
    """Get risk level from data or derive from score."""
    risk = data.get("risk_level")
    if risk:
        return risk
    if score_100 is None:
        return "UNKNOWN"
    if score_100 >= 80:
        return "LOW"
    if score_100 >= 60:
        return "MEDIUM"
    if score_100 >= 40:
        return "HIGH"
    return "CRITICAL"


def format_risk_assessment(scan_result: dict[str, Any]) -> dict[str, Any]:
    """Extract security fields from scan result into focused rug risk output.
    
    Checks actual on-chain security indicators from our API:
    - mint_authority, freeze_authority (Solana)
    - lp_burned_or_locked
    - honeypot detection
    - holder concentration
    - bundle/sniper detection
    - GoPlus trusted status
    - Buy/sell tax
    """
    data = _unwrap_data(scan_result)
    token = _get_token(data)
    score_100 = _get_score_100(data)
    
    risk_factors: list[str] = []
    security_checks: dict[str, Any] = {}
    
    # Mint authority check
    mint_auth = token.get("mint_authority")
    security_checks["mint_authority"] = mint_auth is not None
    if mint_auth is not None:
        risk_factors.append("⚠️ Mint authority active — dev can print unlimited tokens")
    
    # Freeze authority check
    freeze_auth = token.get("freeze_authority")
    security_checks["freeze_authority"] = freeze_auth is not None
    if freeze_auth is not None:
        risk_factors.append("⚠️ Freeze authority active — dev can freeze your wallet")
    
    # LP burned/locked
    lp_safe = token.get("lp_burned_or_locked")
    security_checks["lp_burned_or_locked"] = bool(lp_safe)
    if lp_safe is False:
        risk_factors.append("🚨 Liquidity NOT burned or locked — rug pull possible")
    
    # Honeypot
    is_honeypot = token.get("is_honeypot")
    if is_honeypot is not None:
        security_checks["is_honeypot"] = is_honeypot
        if is_honeypot:
            risk_factors.append("🚨 HONEYPOT DETECTED — you may not be able to sell")
    
    # Holder concentration
    top10 = token.get("top10_holders_pct")
    if top10 is not None:
        security_checks["top10_holders_pct"] = top10
        if top10 >= 80:
            risk_factors.append(f"🚨 Extreme holder concentration: top 10 hold {top10}%")
        elif top10 >= 60:
            risk_factors.append(f"⚠️ High holder concentration: top 10 hold {top10}%")
    
    # Bundle/sniper detection
    bundle = token.get("bundle_detected")
    if bundle is not None:
        security_checks["bundle_detected"] = bundle
        if bundle:
            risk_factors.append("⚠️ Bundle/sniper activity detected at launch")
    
    # GoPlus trusted
    goplus = token.get("goplus_trusted")
    if goplus is not None:
        security_checks["goplus_trusted"] = goplus
    
    # Buy/sell tax
    buy_tax = token.get("buy_tax_pct")
    sell_tax = token.get("sell_tax_pct")
    if buy_tax and float(buy_tax) > 5:
        security_checks["buy_tax_pct"] = buy_tax
        risk_factors.append(f"⚠️ High buy tax: {buy_tax}%")
    if sell_tax and float(sell_tax) > 5:
        security_checks["sell_tax_pct"] = sell_tax
        risk_factors.append(f"⚠️ High sell tax: {sell_tax}%")
    
    # Contract age
    age = token.get("contract_age_days")
    if age is not None:
        security_checks["contract_age_days"] = age
        if age <= 1:
            risk_factors.append("⚠️ Token is less than 24 hours old")
        elif age <= 3:
            risk_factors.append("⚠️ Token is less than 3 days old")
    
    # Transfer hooks (Solana)
    hooks = token.get("transfer_hooks")
    if hooks:
        security_checks["transfer_hooks"] = True
        risk_factors.append("⚠️ Transfer hooks detected — may restrict transfers")
    
    # Determine verdict
    critical_count = sum(1 for f in risk_factors if "🚨" in f)
    warning_count = sum(1 for f in risk_factors if "⚠️" in f)
    
    if critical_count > 0 or (score_100 is not None and score_100 < 40):
        risk_verdict = "DANGER"
    elif warning_count >= 3 or (score_100 is not None and score_100 < 60):
        risk_verdict = "CAUTION"
    elif warning_count > 0:
        risk_verdict = "CAUTION"
    else:
        risk_verdict = "SAFE"
    
    return {
        "risk_verdict": risk_verdict,
        "risk_factors": risk_factors,
        "security_checks": security_checks,
        "score": score_100,
        "grade": score_to_grade(score_100),
    }


def format_quick_score(scan_result: dict[str, Any]) -> dict[str, Any]:
    """Format scan result into minimal score summary."""
    data = _unwrap_data(scan_result)
    token = _get_token(data)
    score_100 = _get_score_100(data)
    risk_level = _get_risk_level(data, score_100)
    
    return {
        "score": score_100,
        "grade": score_to_grade(score_100),
        "risk_level": risk_level,
        "name": token.get("name", "Unknown"),
        "symbol": token.get("symbol", "N/A"),
        "chain": data.get("chain", "unknown"),
        "address": data.get("address", ""),
    }


def format_report_markdown(scan_result: dict[str, Any]) -> str:
    """Generate a comprehensive markdown report from scan results."""
    data = _unwrap_data(scan_result)
    token = _get_token(data)
    score_100 = _get_score_100(data)
    grade = score_to_grade(score_100)
    risk_level = _get_risk_level(data, score_100)
    risk = format_risk_assessment(scan_result)
    
    lines = [
        "# 🔍 VerdictSwarm Token Report",
        "",
        f"**Token:** {token.get('name', 'Unknown')} ({token.get('symbol', 'N/A')})",
        f"**Chain:** {data.get('chain', 'unknown')}",
        f"**Address:** `{data.get('address', 'N/A')}`",
        "",
        f"## Score: {score_100:.0f}/100 (Grade {grade})" if score_100 is not None else "## Score: N/A",
        f"**Risk Level:** {risk_level}",
        f"**Rug Risk:** {risk['risk_verdict']}",
        "",
    ]
    
    # Token metadata
    lines.append("## 📊 Token Metrics")
    if token.get("price_usd"):
        lines.append(f"- **Price:** ${float(token['price_usd']):.6f}")
    if token.get("mcap"):
        lines.append(f"- **Market Cap:** ${float(token['mcap']):,.0f}")
    if token.get("volume_24h"):
        lines.append(f"- **24h Volume:** ${float(token['volume_24h']):,.0f}")
    if token.get("liquidity_usd"):
        lines.append(f"- **Liquidity:** ${float(token['liquidity_usd']):,.0f}")
    if token.get("holder_count"):
        lines.append(f"- **Holders:** {token['holder_count']:,}")
    if token.get("contract_age_days") is not None:
        lines.append(f"- **Contract Age:** {token['contract_age_days']} days")
    lines.append("")
    
    # Security checks
    lines.append("## 🛡️ Security Assessment")
    lines.append(f"**Verdict: {risk['risk_verdict']}**")
    lines.append("")
    
    factors = risk.get("risk_factors", [])
    if factors:
        for f in factors:
            lines.append(f"- {f}")
    else:
        lines.append("- ✅ No major security concerns detected")
    lines.append("")
    
    # Agent verdicts (if available)
    bots = data.get("bots", {})
    if bots:
        lines.append("## 🤖 Agent Analysis")
        for bot_name, verdict in bots.items():
            if isinstance(verdict, dict):
                bot_score = verdict.get("score", "N/A")
                sentiment = verdict.get("sentiment", "N/A")
                reasoning = verdict.get("reasoning", "")
                lines.append(f"### {bot_name}")
                lines.append(f"- **Score:** {bot_score} | **Sentiment:** {sentiment}")
                if reasoning:
                    # Truncate long reasoning
                    short = reasoning[:300] + "..." if len(reasoning) > 300 else reasoning
                    lines.append(f"- {short}")
                lines.append("")
    
    # Locked bots indicator (free tier)
    locked = data.get("locked_bots", [])
    if locked:
        lines.append("## 🔒 Pro Features (Locked)")
        lines.append(f"Upgrade to unlock analysis from: {', '.join(locked)}")
        lines.append("")
    
    # Holder quality
    hq = data.get("holder_quality", {})
    if hq:
        lines.append("## 👥 Holder Quality")
        lines.append(f"- **Score:** {hq.get('score', 'N/A')}/100 (Grade {hq.get('grade', 'N/A')})")
        lines.append("")
    
    lines.append("---")
    lines.append("*Report generated by [VerdictSwarm](https://vswarm.io) — AI-powered crypto risk analysis*")
    
    return "\n".join(lines)
