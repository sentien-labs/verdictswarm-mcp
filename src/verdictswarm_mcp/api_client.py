from __future__ import annotations

from typing import Any

import httpx

from .config import VS_API_KEY, VS_API_URL, VS_TIMEOUT


class VerdictSwarmApiClient:
    def __init__(self, base_url: str = VS_API_URL, api_key: str = VS_API_KEY, timeout: int = VS_TIMEOUT) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers) as client:
                response = await client.request(method, url, **kwargs)
        except httpx.TimeoutException:
            return {"error": "Request timed out. Please try again in a moment."}
        except httpx.RequestError as exc:
            return {"error": f"Network error while contacting VerdictSwarm API: {exc}"}

        if response.status_code == 401:
            return {"error": "Authentication failed. Check your VS_API_KEY."}
        if response.status_code == 429:
            return {"error": "Rate limit exceeded. Please wait and try again."}
        if response.status_code >= 500:
            return {"error": "VerdictSwarm API server error. Please try again later."}

        try:
            data = response.json()
        except ValueError:
            return {"error": "Invalid response from VerdictSwarm API."}

        if response.status_code >= 400:
            message = data.get("error") if isinstance(data, dict) else None
            return {"error": message or f"Request failed with status {response.status_code}."}

        if isinstance(data, dict):
            return data
        return {"data": data}

    async def scan(self, address: str, chain: str = "solana", depth: str = "full", tier: str = "standard") -> dict[str, Any]:
        payload = {
            "address": address,
            "chain": chain,
            "depth": depth,
            "tier": tier,
        }
        return await self._request("POST", "/api/v1/scan", json=payload)

    async def quick_scan(self, address: str, chain: str = "solana") -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/scan/{address}", params={"chain": chain})

    async def get_report(self, address: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/report/{address}")
