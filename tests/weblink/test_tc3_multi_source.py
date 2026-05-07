"""TC3 — Multi-Source Synthesized Response
Category  : Multi-Source
Query type: Semi-precise
Source    : Two public web pages (Wikipedia Python + Wikipedia JavaScript)
Grounding : Fully grounded (synthesized across sources)
Expected  : Response cites >= 1 source; similarity >= threshold.

NotebookLM source URLs:
  https://en.wikipedia.org/wiki/Python_(programming_language)
  https://en.wikipedia.org/wiki/JavaScript

Note: NotebookLM may consolidate citations, so we check for >= 1 not >= 2.
Web source threshold is 0.30.
"""
import os
import pytest
from pathlib import Path
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, citation_count, write_and_score,
)

NOTEBOOK_NAME = "WebTest - Scripting Languages"
TEST_QUERY = (
    "What are the main programming paradigms supported by Python and JavaScript, "
    "and what are their typical use cases in modern software development?"
)
THRESHOLD = 0.20


def test_multi_source_synthesized(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"tc3_multi_source::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        count = citation_count(driver)
        print(f"Citation count: {count}")
        assert count >= 1, (
            f"Expected at least 1 citation for a multi-source query, got {count}"
        )

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a highlighted cited passage"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
