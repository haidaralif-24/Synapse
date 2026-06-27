from __future__ import annotations

import json

from ..state import ResearchState
from ...providers.llm_client import LLMClient

FACT_CHECKER_SYSTEM = """You are a fact-checking assistant. Given a findings summary with URL citations and the original source evidence, identify claims in the summary that are not supported by the evidence.

Return a JSON list of verdicts. Each verdict must have:
- "claim": the unsupported claim text
- "supported": boolean (false if not supported)
- "reason": brief explanation of why it's unsupported
- "source": the relevant source URL or "none"

Only include claims that are NOT supported. If all claims are supported, return an empty list [].

Return ONLY valid JSON."""


def fact_checker_node(state: ResearchState, llm: LLMClient) -> dict:
    evidence_lines = []
    for r in state.search_results:
        evidence_lines.append(f"- [{r['title']}]({r['url']}): {r['snippet']}")

    user_prompt = (
        f"Summary:\n{state.summaries}\n\n"
        f"Original sources:\n{''.join(evidence_lines)}\n\n"
        "Identify unsupported claims. Return only a JSON list."
    )
    response = llm.invoke(
        FACT_CHECKER_SYSTEM, user_prompt,
        response_format={"type": "json_object"},
    )

    try:
        verdicts = json.loads(LLMClient.extract_json(response))
    except (json.JSONDecodeError, ValueError, TypeError):
        verdicts = []

    return {
        "fact_check_verdicts": verdicts,
        "current_stage": "Fact-check complete",
    }
