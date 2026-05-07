"""TC12 — Single-Source Precise
Category  : Single-Source
Query type: Precise
Source    : Public web (Wikipedia — Python programming language)
Grounding : Fully grounded
Expected  : Cited answer; similarity >= threshold.

NotebookLM source URL:
  https://en.wikipedia.org/wiki/Python_(programming_language)
"""
import os
import pytest
from pathlib import Path
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "WebTest - Python Wiki"
TEST_QUERY = "Who created the Python programming language and in what year was it first released?"
THRESHOLD = 0.30
EXPECTED = (
    "Python was created by Guido van Rossum and was first released in 1991."
)


def test_single_source_precise(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"tc12_single_source::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a highlighted cited passage for a fully grounded response"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, EXPECTED, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
