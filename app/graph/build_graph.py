from __future__ import annotations

from langgraph.graph import StateGraph

from .state import ResearchState
from .nodes.planner import planner_node
from .nodes.search import search_node
from .nodes.summarizer import summarizer_node
from .nodes.fact_checker import fact_checker_node
from .nodes.correction import correction_node
from .nodes.writer import writer_node
from ..providers.llm_client import LLMClient
from ..providers.search.base import SearchProvider


def build_pipeline(llm: LLMClient, search_provider: SearchProvider):
    def _planner(state: ResearchState) -> dict:
        return planner_node(state, llm)

    def _search(state: ResearchState) -> dict:
        return search_node(state, search_provider)

    def _summarizer(state: ResearchState) -> dict:
        return summarizer_node(state, llm)

    def _fact_checker(state: ResearchState) -> dict:
        return fact_checker_node(state, llm)

    def _correction(state: ResearchState) -> dict:
        return correction_node(state, llm)

    def _writer(state: ResearchState) -> dict:
        return writer_node(state, llm)

    builder = StateGraph(ResearchState)

    builder.add_node("planner", _planner)
    builder.add_node("search", _search)
    builder.add_node("summarizer", _summarizer)
    builder.add_node("fact_checker", _fact_checker)
    builder.add_node("correction", _correction)
    builder.add_node("writer", _writer)

    builder.set_entry_point("planner")
    builder.add_edge("planner", "search")
    builder.add_edge("search", "summarizer")
    builder.add_edge("summarizer", "fact_checker")
    builder.add_edge("fact_checker", "correction")
    builder.add_edge("correction", "writer")

    return builder.compile()
