from __future__ import annotations

from ..state import ResearchState
from ...providers.llm_client import LLMClient

WRITER_SYSTEM = """You are a research findings document writer. Given sub-questions, source-backed summaries with URLs, and a correction log, produce a findings document — NOT a prose essay or paper.

Structure:
- **Title** — the research topic
- **Key Findings** — for each finding, list the claim followed by every source that supports it. Each source must include its full URL as a clickable markdown link.
- **Sources** — numbered bibliography at the end with the full URL for every reference.

Rules:
- Every claim MUST be followed by at least one `[source](url)` inline citation.
- Do NOT write paragraphs that mix claims from different sources without attribution.
- If a source had to be corrected, note it inline.
- Never fabricate a URL — only use URLs from the provided evidence."""


def writer_node(state: ResearchState, llm: LLMClient) -> dict:
    evidence_lines = []
    for r in state.search_results:
        evidence_lines.append(f"- [{r['title']}]({r['url']}): {r['snippet']}")

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
        f"All source evidence with URLs:\n{''.join(evidence_lines)}\n\n"
        f"Correction log:{correction_section}\n\n"
        "Write the final findings document. Every claim must cite its source URL."
    )
    report = llm.invoke(WRITER_SYSTEM, user_prompt, temperature=0.3)

    return {
        "final_report": report,
        "current_stage": "Report complete",
    }
