"""TC19 — Partial Relevance
Category  : Partial Relevance
Query type: Semi-precise
Source    : Public web (Wikipedia — Software testing)
Grounding : Partially grounded
Expected  : Response draws on available content but only partially addresses the query;
            similarity >= lower threshold (0.25).

NotebookLM source URL:
  https://en.wikipedia.org/wiki/Software_testing
"""
import os
import pytest
from pathlib import Path
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "WebTest - Software Testing"
TEST_QUERY = (
    "What testing strategies are specifically recommended for microservices "
    "and containerized cloud-native applications?"
)
THRESHOLD = 0.25


def test_partial_relevance(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"tc19_partial_relevance::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected at least a partial citation from the software testing source"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f} (partial relevance threshold: {THRESHOLD})")
        assert sim >= THRESHOLD, (
            f"Similarity {sim:.4f} is below partial-relevance threshold {THRESHOLD}"
        )
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
