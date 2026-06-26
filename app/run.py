"""
CLI entry point to run the research pipeline headless (no GUI).

Usage:
    python -m app.run "Your research topic here"

Requires an API key to be configured (run the GUI once to set it up,
or set the DISTILLERY_API_KEY environment variable).
"""
from __future__ import annotations

import json
import os
import sys

from .config import get_api_key, get_model, get_provider
from .graph.build_graph import build_pipeline
from .graph.state import ResearchState
from .providers.llm_client import LLMClient
from .providers.search.duckduckgo import DuckDuckGoProvider


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.run \"Your research topic\"", file=sys.stderr)
        sys.exit(1)

    topic = sys.argv[1]

    api_key = os.environ.get("DISTILLERY_API_KEY") or get_api_key()
    if not api_key:
        print("Error: No API key found.", file=sys.stderr)
        print("Set DISTILLERY_API_KEY env var, or run the GUI first to configure one.", file=sys.stderr)
        sys.exit(1)

    provider = os.environ.get("DISTILLERY_PROVIDER") or get_provider()

    model = os.environ.get("DISTILLERY_MODEL") or get_model()
    llm = LLMClient(provider=provider, api_key=api_key, model=model or None)
    search = DuckDuckGoProvider()
    graph = build_pipeline(llm, search)

    state = ResearchState(topic=topic)

    tracked = {
        "topic": topic,
        "sub_questions": [],
        "outline": "",
        "search_results": [],
        "summaries": "",
        "fact_check_verdicts": [],
        "correction_log": [],
        "final_report": "",
        "current_stage": "",
    }

    print(f"Researching: {topic}")
    print(f"Provider: {provider}")
    print()

    for event in graph.stream(state, stream_mode="updates"):
        if isinstance(event, dict):
            for node_name, updates in event.items():
                if isinstance(updates, dict):
                    tracked.update(updates)
                    stage = updates.get("current_stage", "running...")
                    print(f"  [{node_name}] {stage}")

    for key, val in tracked.items():
        setattr(state, key, val)

    print()
    print("=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(state.final_report)


if __name__ == "__main__":
    main()
