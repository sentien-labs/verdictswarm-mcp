from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from verdictswarm_mcp.api_client import VerdictSwarmApiClient


def _make_response(status_code: int, json_data=None, json_error=None):
    """Create a mock httpx.Response (sync .json(), sync .status_code)."""
    resp = MagicMock()
    resp.status_code = status_code
    if json_error:
        resp.json.side_effect = json_error
    else:
        resp.json.return_value = json_data
    return resp


@pytest.mark.asyncio
async def test_scan_success_with_api_key(mock_scan_result):
    response = _make_response(200, mock_scan_result)
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient(api_key="secret-key")
        result = await client.scan(address="So111", chain="solana", depth="full", tier="standard")

    assert result == mock_scan_result
    _, kwargs = mock_cls.call_args
    assert kwargs["headers"]["x-api-key"] == "secret-key"


@pytest.mark.asyncio
async def test_scan_success_without_api_key(mock_scan_result):
    response = _make_response(200, mock_scan_result)
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient(api_key="")
        await client.scan(address="So111")

    _, kwargs = mock_cls.call_args
    assert "x-api-key" not in kwargs["headers"]


@pytest.mark.asyncio
async def test_request_timeout_returns_error():
    client_ctx = AsyncMock()
    client_ctx.request.side_effect = httpx.TimeoutException("timeout")

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient()
        result = await client.scan(address="So111")

    assert "timed out" in result["error"].lower()


@pytest.mark.asyncio
async def test_request_429_returns_rate_limit_error():
    response = _make_response(429, {"error": "too many requests"})
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient()
        result = await client.scan(address="So111")

    assert "Rate limit exceeded" in result["error"]


@pytest.mark.asyncio
async def test_request_401_returns_auth_error():
    response = _make_response(401, {"error": "unauthorized"})
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient()
        result = await client.scan(address="So111")

    assert "Authentication failed" in result["error"]


@pytest.mark.asyncio
async def test_request_500_returns_server_error():
    response = _make_response(500, {"error": "server down"})
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient()
        result = await client.scan(address="So111")

    assert "server error" in result["error"].lower()


@pytest.mark.asyncio
async def test_request_400_uses_error_message_from_response():
    response = _make_response(400, {"error": "bad payload"})
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient()
        result = await client.scan(address="So111")

    assert result == {"error": "bad payload"}


@pytest.mark.asyncio
async def test_scan_calls_pay_swarm_endpoint(mock_scan_result):
    response = _make_response(200, mock_scan_result)
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient(base_url="https://api.example.com")
        await client.scan(address="TokenAddr", chain="base")

    client_ctx.request.assert_awaited_once_with(
        "POST",
        "https://api.example.com/api/v1/pay/scan/swarm",
        json={"address": "TokenAddr", "chain": "base"},
    )


@pytest.mark.asyncio
async def test_quick_scan_calls_basic_pay_endpoint(mock_scan_result):
    response = _make_response(200, mock_scan_result)
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient(base_url="https://api.example.com")
        await client.quick_scan(address="TokenAddr", chain="base")

    client_ctx.request.assert_awaited_once_with(
        "POST",
        "https://api.example.com/api/v1/pay/scan/basic",
        json={"address": "TokenAddr", "chain": "base"},
    )


@pytest.mark.asyncio
async def test_rug_risk_scan_calls_pro_pay_endpoint(mock_scan_result):
    response = _make_response(200, mock_scan_result)
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient(base_url="https://api.example.com")
        await client.rug_risk_scan(address="TokenAddr", chain="ethereum")

    client_ctx.request.assert_awaited_once_with(
        "POST",
        "https://api.example.com/api/v1/pay/scan/pro",
        json={"address": "TokenAddr", "chain": "ethereum"},
    )


@pytest.mark.asyncio
async def test_payment_signature_header_is_sent():
    response = _make_response(200, {"ok": True})
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient(base_url="https://api.example.com", api_key="")
        await client.quick_scan(address="TokenAddr", chain="solana", payment_signature="tx123")

    _, kwargs = mock_cls.call_args
    assert kwargs["headers"]["x-payment-signature"] == "tx123"


@pytest.mark.asyncio
async def test_request_402_returns_payment_instructions():
    payment_detail = {
        "price_usd": "1.00",
        "payment_address": "0xabc",
        "endpoint": "/api/v1/pay/scan/swarm",
    }
    response = _make_response(402, {"detail": payment_detail})
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient()
        result = await client.scan(address="So111")

    assert result["payment_required"] is True
    assert result["status_code"] == 402
    assert result["payment_instructions"] == payment_detail
    assert "Payment required" in result["error"]


@pytest.mark.asyncio
async def test_invalid_json_returns_error():
    response = _make_response(200, json_error=ValueError("not json"))
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient()
        result = await client.scan(address="So111")

    assert result == {"error": "Invalid response from VerdictSwarm API."}


@pytest.mark.asyncio
async def test_get_report_endpoint_path(mock_scan_result):
    response = _make_response(200, mock_scan_result)
    client_ctx = AsyncMock()
    client_ctx.request.return_value = response

    with patch("verdictswarm_mcp.api_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = client_ctx
        client = VerdictSwarmApiClient(base_url="https://api.example.com")
        await client.get_report(address="Addr123")

    client_ctx.request.assert_awaited_once_with("GET", "https://api.example.com/api/report/Addr123")
