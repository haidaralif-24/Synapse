from __future__ import annotations

from ..state import ResearchState
from ...providers.llm_client import LLMClient

PLANNER_SYSTEM = """You are a research planning assistant. Given a topic, break it down into 3-6 sub-questions and produce a short report outline.

Return your response in exactly this format:

SUB-QUESTIONS:
1. <sub-question 1>
2. <sub-question 2>
...

OUTLINE:
<brief outline>"""


def planner_node(state: ResearchState, llm: LLMClient) -> dict:
    user_prompt = f"Research topic: {state.topic}\n\nBreak this topic into sub-questions and provide a report outline."
    response = llm.invoke(PLANNER_SYSTEM, user_prompt)

    sub_questions = []
    outline_parts = []
    in_questions = False
    in_outline = False

    for line in response.split("\n"):
        stripped = line.strip()
        if "SUB-QUESTIONS" in stripped:
            in_questions = True
            in_outline = False
            continue
        if "OUTLINE" in stripped:
            in_questions = False
            in_outline = True
            continue
        if in_questions and stripped:
            cleaned = stripped
            if cleaned[0].isdigit() and ". " in cleaned:
                cleaned = cleaned.split(". ", 1)[-1]
            sub_questions.append(cleaned)
        if in_outline and stripped:
            outline_parts.append(stripped)

    return {
        "sub_questions": sub_questions,
        "outline": "\n".join(outline_parts),
        "current_stage": "Planning complete",
    }
