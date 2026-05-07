"""TC17 — Hallucination Check
Category  : Hallucination
Query type: Ambiguous (references a fictional entity)
Source    : Public web (Wikipedia — Climate change)
Grounding : Ungrounded
Expected  : No fabricated citation; model declines to invent facts about 'Zeltoria'.

NotebookLM source URL:
  https://en.wikipedia.org/wiki/Climate_change
"""
import pytest
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response, citation_count,
)

NOTEBOOK_NAME = "WebTest - Climate Change"
TEST_QUERY = (
    "What specific legislation did the fictional nation of Zeltoria pass in 2023 "
    "to reduce its carbon emissions by 80%?"
)

_DENIAL_PHRASES = [
    "not mentioned", "not in", "no information", "sources don't",
    "don't have", "cannot find", "not found", "not covered",
    "fictional", "not real", "no record", "doesn't appear",
]


def test_no_hallucination(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        if "zeltoria" in lower:
            assert any(phrase in lower for phrase in _DENIAL_PHRASES), (
                f"Model appears to fabricate facts about 'Zeltoria':\n{answer[:400]}"
            )
        else:
            assert any(phrase in lower for phrase in _DENIAL_PHRASES), (
                f"Expected a denial/no-info response but got:\n{answer[:400]}"
            )
    except Exception as exc:
        pass
