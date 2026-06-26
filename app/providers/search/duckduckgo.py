from __future__ import annotations

from typing import List

from ddgs import DDGS

from .base import SearchProvider, SearchResult


class DuckDuckGoProvider(SearchProvider):
    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        results: List[SearchResult] = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                ))
        return results
