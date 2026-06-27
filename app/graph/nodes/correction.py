from __future__ import annotations

from ..state import ResearchState, CorrectionEntry
from ...providers.llm_client import LLMClient

CORRECTION_SYSTEM = """You are a research correction assistant. Given flagged unsupported claims, the original summaries, and source evidence, produce corrected summaries. For each flagged claim, either fix it with source-backed information or remove it entirely. Return ONLY the corrected summary text with no additional commentary."""


def correction_node(state: ResearchState, llm: LLMClient) -> dict:
    if not state.fact_check_verdicts:
        return {"current_stage": "No corrections needed", "correction_log": []}

    evidence_lines = []
    for r in state.search_results:
        evidence_lines.append(f"- [{r['title']}]({r['url']}): {r['snippet']}")

    flagged_lines = []
    for v in state.fact_check_verdicts:
        flagged_lines.append(f"- {v.get('claim', '')} (reason: {v.get('reason', '')})")

    user_prompt = (
        f"Original summaries:\n{state.summaries}\n\n"
        f"Flagged unsupported claims:\n{''.join(flagged_lines)}\n\n"
        f"Evidence:\n{''.join(evidence_lines)}\n\n"
        "Return the corrected version of the summaries with every flagged claim either fixed using the evidence or removed."
    )
    corrected_summaries = llm.invoke(CORRECTION_SYSTEM, user_prompt)

    correction_log = []
    for v in state.fact_check_verdicts:
        correction_log.append(CorrectionEntry(
            claim=v.get("claim", ""),
            reason=v.get("reason", ""),
            corrected=f"[Struck: {v.get('reason', 'unsupported')}]",
            source=v.get("source", "none"),
        ))

    return {
        "correction_log": correction_log,
        "summaries": corrected_summaries,
        "current_stage": "Correction complete",
    }
