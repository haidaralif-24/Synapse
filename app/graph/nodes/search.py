from __future__ import annotations

from typing import List

from ..state import ResearchState
from ...providers.search.base import SearchProvider


def search_node(state: ResearchState, search_provider: SearchProvider) -> dict:
    queries = state.sub_questions[:]
    queries.append(state.topic)

    all_results: List[dict] = []
    for q in queries:
        results = search_provider.search(q, num_results=4)
        for r in results:
            all_results.append({
                "query": q,
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
            })

    return {
        "search_results": all_results,
        "current_stage": "Search complete",
    }
