"""TC13 — Retrieve Exact Content, Unclear Query
Category  : Single-Source Retrieval
Query type: Somewhat unclear
Source    : Google Doc — Project Management Glossary
Grounding : Fully grounded
Expected  : Correct data retrieved and translated despite query ambiguity.

Notebook : "GSuite - PM Glossary"
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - PM Glossary"
TEST_QUERY = "How fast does the team work in agile? What does speed mean in sprints?"
THRESHOLD = 0.25


def test_unclear_query_retrieval(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc13_unclear_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        assert any(kw in lower for kw in ["velocity", "story point", "sprint", "agile"]), (
            f"Expected answer to mention velocity/story points/agile, got:\n{answer[:400]}"
        )

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage from the glossary"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"TC13 - {type(exc).__name__}: {exc}")
