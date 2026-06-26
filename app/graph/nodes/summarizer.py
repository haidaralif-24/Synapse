from __future__ import annotations

from ..state import ResearchState
from ...providers.llm_client import LLMClient

SUMMARIZER_SYSTEM = """You are a research summarizer. Given search results for a set of sub-questions, produce a concise, grounded summary for each sub-question. Cite sources by URL inline."""


def summarizer_node(state: ResearchState, llm: LLMClient) -> dict:
    evidence_lines = []
    for r in state.search_results:
        evidence_lines.append(f"- [{r['title']}]({r['url']}): {r['snippet']}")

    sub_questions_text = "\n".join(f"- {q}" for q in state.sub_questions)

    user_prompt = (
        f"Sub-questions:\n{sub_questions_text}\n\n"
        f"Evidence:\n{''.join(evidence_lines)}\n\n"
        "Produce grounded per-sub-question summaries."
    )
    summary = llm.invoke(SUMMARIZER_SYSTEM, user_prompt)

    return {
        "summaries": summary,
        "current_stage": "Summarization complete",
    }
