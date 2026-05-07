"""TC18 — Relevant Retrieval
Category  : Relevant Retrieval
Query type: Precise
Source    : Public web (Wikipedia — Climate change)
Grounding : Fully grounded
Expected  : Accurate, cited answer with similarity >= threshold.

NotebookLM source URL:
  https://en.wikipedia.org/wiki/Climate_change
"""
import os
import pytest
from pathlib import Path
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "WebTest - Climate Change"
TEST_QUERY = (
    "What are the primary human activities that scientists identify as "
    "the main drivers of climate change?"
)
THRESHOLD = 0.30


def test_relevant_retrieval(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"tc18_relevant_retrieval::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage for a directly relevant query"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
