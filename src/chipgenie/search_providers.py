from __future__ import annotations

import os
from typing import Dict, List, Optional

import httpx
from pydantic import BaseModel
from dotenv import load_dotenv


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None


class SearchConfig(BaseModel):
    provider: str = "stub"  # serpapi|stub
    serpapi_key: Optional[str] = None


class SearchClient:
    def __init__(self, config: Optional[SearchConfig] = None):
        load_dotenv()
        provider = os.getenv("CHIPGENIE_SEARCH_PROVIDER", "stub")
        self.config = config or SearchConfig(
            provider=provider,
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
        )

    async def search(self, query: str) -> List[SearchResult]:
        if self.config.provider == "serpapi":
            return await self._search_serpapi(query)
        return self._search_stub(query)

    def _search_stub(self, query: str) -> List[SearchResult]:
        return [
            SearchResult(title="Octopart Search", url=f"https://octopart.com/search?q={query}"),
            SearchResult(title="Mouser Search", url=f"https://www.mouser.com/c/?q={query}"),
        ]

    async def _search_serpapi(self, query: str) -> List[SearchResult]:
        key = self.config.serpapi_key
        if not key:
            return self._search_stub(query)
        params: Dict[str, str] = {
            "engine": "google",
            "q": query,
            "api_key": key,
            "num": "10",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get("https://serpapi.com/search", params=params)
            resp.raise_for_status()
            data = resp.json()
            results: List[SearchResult] = []
            for item in data.get("organic_results", [])[:10]:
                results.append(
                    SearchResult(title=item.get("title", ""), url=item.get("link", ""), snippet=item.get("snippet"))
                )
            return results
