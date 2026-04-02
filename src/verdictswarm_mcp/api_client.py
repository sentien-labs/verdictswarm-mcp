from __future__ import annotations

from typing import Any

import httpx

from .config import VS_API_KEY, VS_API_URL, VS_MCP_SERVICE_KEY, VS_TIMEOUT


class VerdictSwarmApiClient:
    def __init__(self, base_url: str = VS_API_URL, api_key: str = VS_MCP_SERVICE_KEY or VS_API_KEY, timeout: int = VS_TIMEOUT) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self, payment_signature: str = "") -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        if payment_signature:
            headers["x-payment-signature"] = payment_signature
        return headers

    async def _request(self, method: str, path: str, payment_signature: str = "", **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers(payment_signature=payment_signature)) as client:
                response = await client.request(method, url, **kwargs)
        except httpx.TimeoutException:
            return {"error": "Request timed out. Please try again in a moment."}
        except httpx.RequestError as exc:
            return {"error": f"Network error while contacting VerdictSwarm API: {exc}"}

        if response.status_code == 401:
            return {"error": "Authentication failed. Check your VS_API_KEY."}
        if response.status_code == 429:
            return {"error": "Rate limit exceeded. Please wait and try again."}
        try:
            data = response.json()
        except ValueError:
            return {"error": "Invalid response from VerdictSwarm API."}

        if response.status_code == 402:
            details = data.get("detail") if isinstance(data, dict) else {}
            instructions = details if isinstance(details, dict) else {}
            return {
                "error": "Payment required.",
                "payment_required": True,
                "status_code": 402,
                "payment_instructions": instructions,
            }
        if response.status_code >= 500:
            return {"error": "VerdictSwarm API server error. Please try again later."}
        if response.status_code >= 400:
            message = data.get("error") if isinstance(data, dict) else None
            return {"error": message or f"Request failed with status {response.status_code}."}

        if isinstance(data, dict):
            return data
        return {"data": data}

    async def scan(
        self,
        address: str,
        chain: str = "solana",
        depth: str = "full",
        tier: str = "PRO_PLUS",
        payment_signature: str = "",
    ) -> dict[str, Any]:
        del depth, tier  # Pay-lane endpoint controls depth/tier server-side.
        payload = {"address": address, "chain": chain}
        return await self._request("POST", "/api/v1/pay/scan/swarm", payment_signature=payment_signature, json=payload)

    async def quick_scan(self, address: str, chain: str = "solana", payment_signature: str = "") -> dict[str, Any]:
        payload = {"address": address, "chain": chain}
        return await self._request("POST", "/api/v1/pay/scan/basic", payment_signature=payment_signature, json=payload)

    async def rug_risk_scan(self, address: str, chain: str = "solana", payment_signature: str = "") -> dict[str, Any]:
        payload = {"address": address, "chain": chain}
        return await self._request("POST", "/api/v1/pay/scan/pro", payment_signature=payment_signature, json=payload)

    async def get_report(self, address: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/report/{address}")


VerdictSwarmClient = VerdictSwarmApiClient  # Convenience alias
