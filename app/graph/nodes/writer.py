from __future__ import annotations

from ..state import ResearchState
from ...providers.llm_client import LLMClient

WRITER_SYSTEM = """You are a research report writer. Given sub-questions, summaries, and a correction log, produce a well-structured markdown report with inline citations."""


def writer_node(state: ResearchState, llm: LLMClient) -> dict:
    correction_section = ""
    if state.correction_log:
        lines = ["\n\n## Unverified Claims\n\nThe following claims could not be verified:\n"]
        for entry in state.correction_log:
            lines.append(f"- **{entry.claim}** — {entry.reason} (source: {entry.source})")
        correction_section = "".join(lines)

    user_prompt = (
        f"Topic: {state.topic}\n\n"
        f"Outline: {state.outline}\n\n"
        f"Summaries:\n{state.summaries}\n\n"
        f"Correction log:{correction_section}\n\n"
        "Write the final markdown report."
    )
    report = llm.invoke(WRITER_SYSTEM, user_prompt, temperature=0.3)

    return {
        "final_report": report,
        "current_stage": "Report complete",
    }
