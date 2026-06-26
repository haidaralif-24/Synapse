from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.graph.state import ResearchState, CorrectionEntry
from app.providers.search.base import SearchResult


def test_state_defaults():
    state = ResearchState(topic="test topic")
    assert state.topic == "test topic"
    assert state.sub_questions == []
    assert state.outline == ""
    assert state.search_results == []
    assert state.summaries == ""
    assert state.fact_check_verdicts == []
    assert state.correction_log == []
    assert state.final_report == ""
    assert state.current_stage == ""


def test_correction_entry():
    entry = CorrectionEntry(
        claim="Claim X",
        reason="Not supported",
        corrected="[Struck: Not supported]",
        source="https://example.com",
    )
    assert entry.claim == "Claim X"
    assert entry.reason == "Not supported"


@patch("app.providers.search.duckduckgo.DDGS")
def test_duckduckgo_provider(mock_ddgs):
    from app.providers.search.duckduckgo import DuckDuckGoProvider

    mock_instance = MagicMock()
    mock_instance.text.return_value = [
        {"title": "Result 1", "href": "https://example.com/1", "body": "Snippet 1"},
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_instance

    provider = DuckDuckGoProvider()
    results = provider.search("test query", num_results=1)

    assert len(results) == 1
    assert results[0].title == "Result 1"
    assert results[0].url == "https://example.com/1"
    assert results[0].snippet == "Snippet 1"


@patch("app.providers.llm_client.OpenAI")
def test_llm_client(mock_openai):
    from app.providers.llm_client import LLMClient

    mock_instance = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello from LLM"
    mock_instance.chat.completions.create.return_value.choices = [mock_choice]
    mock_openai.return_value = mock_instance

    client = LLMClient(provider="openai", api_key="test-key")
    result = client.invoke("system prompt", "user prompt")

    assert result == "Hello from LLM"
    mock_instance.chat.completions.create.assert_called_once()


def test_planner_node_parses_response():
    from app.graph.nodes.planner import planner_node

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = (
        "SUB-QUESTIONS:\n"
        "1. What is X?\n"
        "2. How does Y work?\n"
        "\n"
        "OUTLINE:\n"
        "Introduction\nBody\nConclusion"
    )

    state = ResearchState(topic="Test topic")
    result = planner_node(state, mock_llm)

    assert "sub_questions" in result
    assert len(result["sub_questions"]) == 2
    assert result["sub_questions"][0] == "What is X?"
    assert "outline" in result
    assert "Introduction" in result["outline"]


def test_search_node():
    from app.graph.nodes.search import search_node

    mock_provider = MagicMock()
    mock_provider.search.return_value = [
        SearchResult(title="T1", url="https://a.com", snippet="Snippet 1"),
    ]

    state = ResearchState(topic="Test", sub_questions=["Q1", "Q2"])
    result = search_node(state, mock_provider)

    assert len(result["search_results"]) == 3  # Q1, Q2 + topic
    assert result["search_results"][0]["title"] == "T1"
    assert mock_provider.search.call_count == 3


def test_fact_checker_parses_json():
    from app.graph.nodes.fact_checker import fact_checker_node

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = '[{"claim": "Bad claim", "supported": false, "reason": "No source", "source": "none"}]'

    state = ResearchState(
        topic="Test",
        summaries="Some summary text",
        search_results=[{"title": "S", "url": "https://x.com", "snippet": "content"}],
    )
    result = fact_checker_node(state, mock_llm)

    assert len(result["fact_check_verdicts"]) == 1
    assert result["fact_check_verdicts"][0]["claim"] == "Bad claim"


def test_writer_node():
    from app.graph.nodes.writer import writer_node

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = "# Final Report\n\nContent here."

    state = ResearchState(
        topic="Test",
        outline="Outline here",
        summaries="Summaries here",
        correction_log=[
            CorrectionEntry(claim="C1", reason="Unsupported", corrected="[Struck]", source="src")
        ],
    )
    result = writer_node(state, mock_llm)

    assert "final_report" in result
    assert result["final_report"] == "# Final Report\n\nContent here."
