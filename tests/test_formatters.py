import pytest

from verdictswarm_mcp.formatters import (
    format_quick_score,
    format_report_markdown,
    format_risk_assessment,
    score_to_grade,
)


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, "F"),
        (39, "F"),
        (40, "D"),
        (59, "D"),
        (60, "C"),
        (69, "C"),
        (70, "B"),
        (79, "B"),
        (80, "A"),
        (100, "A"),
        (None, "N/A"),
    ],
)
def test_score_to_grade_boundaries(score, expected):
    assert score_to_grade(score) == expected


def test_format_risk_assessment_safe_token(mock_scan_result):
    result = format_risk_assessment(mock_scan_result)
    assert result["risk_verdict"] == "SAFE"
    assert result["risk_factors"] == []
    assert result["score"] == 67.0
    assert result["grade"] == "C"


def test_format_risk_assessment_danger_token(mock_dangerous_result):
    result = format_risk_assessment(mock_dangerous_result)
    assert result["risk_verdict"] == "DANGER"
    assert len(result["risk_factors"]) >= 4
    assert any("HONEYPOT" in factor for factor in result["risk_factors"])
    assert any("Liquidity NOT burned or locked" in factor for factor in result["risk_factors"])


def test_format_risk_assessment_missing_token_fields_graceful(mock_scan_result):
    partial = {"data": {**mock_scan_result["data"], "token": {"name": "OnlyName"}}}
    result = format_risk_assessment(partial)
    assert result["risk_verdict"] in {"SAFE", "CAUTION"}
    assert isinstance(result["risk_factors"], list)
    assert isinstance(result["security_checks"], dict)


def test_format_quick_score_returns_expected_fields(mock_scan_result):
    quick = format_quick_score(mock_scan_result)
    assert quick["score"] == 67.0
    assert quick["grade"] == "C"
    assert quick["risk_level"] == "MEDIUM"
    assert quick["name"] == "Sample Token"
    assert quick["symbol"] == "SMPL"
    assert quick["chain"] == "solana"


def test_format_quick_score_derives_defaults_when_missing():
    quick = format_quick_score({"data": {"score": 8.2}})
    assert quick["score"] == 82.0
    assert quick["grade"] == "A"
    assert quick["name"] == "Unknown"
    assert quick["symbol"] == "N/A"
    assert quick["chain"] == "unknown"


def test_format_quick_score_uses_free_tier_confidence(mock_free_result):
    quick = format_quick_score(mock_free_result)
    assert quick["score"] == 67.0
    assert quick["grade"] == "C"
    assert quick["risk_level"] == "MEDIUM"


def test_format_report_markdown_contains_key_sections(mock_scan_result):
    report = format_report_markdown(mock_scan_result)
    assert "# 🔍 VerdictSwarm Token Report" in report
    assert "## Score:" in report
    assert "## 🛡️ Security Assessment" in report
    assert "## 📊 Token Metrics" in report


def test_format_report_markdown_includes_locked_bots_section(mock_free_result):
    report = format_report_markdown(mock_free_result)
    assert "## 🔒 Pro Features (Locked)" in report
    assert "whale_guard" in report


def test_format_report_markdown_no_risk_factors_shows_safe_line(mock_scan_result):
    report = format_report_markdown(mock_scan_result)
    assert "✅ No major security concerns detected" in report


def test_format_report_markdown_with_dangerous_token_contains_red_flags(mock_dangerous_result):
    report = format_report_markdown(mock_dangerous_result)
    assert "**Verdict: DANGER**" in report
    assert "HONEYPOT DETECTED" in report


def test_format_risk_assessment_caution_from_warnings(mock_scan_result):
    warning_case = {"data": {**mock_scan_result["data"], "token": {**mock_scan_result["data"]["token"], "contract_age_days": 1, "bundle_detected": True, "top10_holders_pct": 65}}}
    result = format_risk_assessment(warning_case)
    assert result["risk_verdict"] == "CAUTION"
    assert len(result["risk_factors"]) >= 3
