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

    provider = os.environ.get("SYNAPSE_PROVIDER") or get_provider()

    api_key = os.environ.get("SYNAPSE_API_KEY") or get_api_key(provider)
    if not api_key:
        print("Error: No API key found.", file=sys.stderr)
        print("Set SYNAPSE_API_KEY env var, or run the GUI first to configure one.", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("SYNAPSE_MODEL") or get_model()
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
