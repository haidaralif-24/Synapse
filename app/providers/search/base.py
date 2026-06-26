from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    content: str = ""


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        ...
