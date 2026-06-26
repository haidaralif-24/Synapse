from __future__ import annotations

from typing import List

from tavily import TavilyClient

from .base import SearchProvider, SearchResult


class TavilyProvider(SearchProvider):
    def __init__(self, api_key: str):
        self._client = TavilyClient(api_key=api_key)

    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        resp = self._client.search(query, max_results=num_results)
        return [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("content", ""),
            )
            for r in resp.get("results", [])
        ]
