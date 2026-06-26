from __future__ import annotations

from ..state import ResearchState, CorrectionEntry
from ...providers.llm_client import LLMClient

CORRECTION_SYSTEM = """You are a research correction assistant. Given flagged unsupported claims and the original source evidence, produce corrected text. For each claim, either fix it with source-backed information or mark it for removal."""


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
        f"Summary:\n{state.summaries}\n\n"
        f"Flagged claims:\n{''.join(flagged_lines)}\n\n"
        f"Evidence:\n{''.join(evidence_lines)}\n\n"
        "Produce corrections."
    )
    llm.invoke(CORRECTION_SYSTEM, user_prompt)

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
        "current_stage": "Correction complete",
    }
