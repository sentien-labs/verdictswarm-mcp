from unittest.mock import AsyncMock, patch

import pytest

from verdictswarm_mcp.server import (
    check_rug_risk,
    get_quick_score,
    get_token_report,
    get_trending_risky,
    mcp,
    scan_token,
)


@pytest.mark.asyncio
async def test_scan_token_returns_api_result(mock_scan_result):
    scan_mock = AsyncMock(return_value=mock_scan_result)
    with patch("verdictswarm_mcp.server.api_client.scan", scan_mock):
        result = await scan_token("So111", chain="solana", depth="full")
    assert result == mock_scan_result
    scan_mock.assert_awaited_once_with(
        address="So111",
        chain="solana",
        depth="full",
        tier="PRO_PLUS",
        payment_signature="",
    )


@pytest.mark.asyncio
async def test_get_quick_score_formats_result(mock_scan_result):
    with patch("verdictswarm_mcp.server.api_client.quick_scan", AsyncMock(return_value=mock_scan_result)):
        result = await get_quick_score("So111", chain="solana")
    assert result["score"] == 67.0
    assert result["grade"] == "C"
    assert result["symbol"] == "SMPL"


@pytest.mark.asyncio
async def test_get_quick_score_propagates_error():
    with patch("verdictswarm_mcp.server.api_client.quick_scan", AsyncMock(return_value={"error": "boom"})):
        result = await get_quick_score("So111")
    assert result == {"error": "boom"}


@pytest.mark.asyncio
async def test_get_quick_score_propagates_payment_required():
    payment_error = {
        "error": "Payment required.",
        "payment_required": True,
        "status_code": 402,
        "payment_instructions": {"price_usd": "0.10"},
    }
    with patch("verdictswarm_mcp.server.api_client.quick_scan", AsyncMock(return_value=payment_error)):
        result = await get_quick_score("So111")
    assert result == payment_error


@pytest.mark.asyncio
async def test_check_rug_risk_returns_assessment(mock_dangerous_result):
    with patch("verdictswarm_mcp.server.api_client.rug_risk_scan", AsyncMock(return_value=mock_dangerous_result)):
        result = await check_rug_risk("Bad111")
    assert result["risk_verdict"] == "DANGER"
    assert isinstance(result["risk_factors"], list)


@pytest.mark.asyncio
async def test_check_rug_risk_propagates_error():
    with patch("verdictswarm_mcp.server.api_client.rug_risk_scan", AsyncMock(return_value={"error": "timeout"})):
        result = await check_rug_risk("Bad111")
    assert result == {"error": "timeout"}


@pytest.mark.asyncio
async def test_get_trending_risky_returns_coming_soon():
    result = await get_trending_risky(chain="base", min_risk_level="HIGH", limit=999)
    assert result["status"] == "coming_soon"
    assert result["chain"] == "base"
    assert result["limit"] == 20


@pytest.mark.asyncio
async def test_get_token_report_returns_markdown(mock_scan_result):
    with patch("verdictswarm_mcp.server.api_client.quick_scan", AsyncMock(return_value=mock_scan_result)):
        report = await get_token_report("So111")
    assert report.startswith("# 🔍 VerdictSwarm Token Report")
    assert "Sample Token" in report


@pytest.mark.asyncio
async def test_get_token_report_error_markdown():
    with patch("verdictswarm_mcp.server.api_client.quick_scan", AsyncMock(return_value={"error": "not found"})):
        report = await get_token_report("Missing")
    assert report.startswith("# VerdictSwarm Token Report")
    assert "Error: not found" in report


def test_mcp_object_exists():
    assert mcp is not None
