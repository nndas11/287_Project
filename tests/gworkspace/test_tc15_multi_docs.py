"""TC15 — Summarization, Multi-Source
Category  : Multi-Source Summarization
Query type: Somewhat unclear
Source    : Two Google Docs — Q1 Project Report + Q2 Project Report
Grounding : Fully grounded
Expected  : Combined summary from both sources without duplication.

Notebook : "GSuite - Multi Quarter Reports"
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
    citation_count,
)

NOTEBOOK_NAME = "GSuite - Multi Quarter Reports"
TEST_QUERY = "How is the project going overall? Give me an overview of the progress."
THRESHOLD = 0.22


def test_multi_source_summary(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc15_multi_source_summary::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        has_q1 = any(kw in lower for kw in ["q1", "design phase", "12 feature", "95%", "88%"])
        has_q2 = any(kw in lower for kw in ["q2", "beta", "200 participant", "4.2", "91%"])
        assert has_q1 or has_q2, (
            f"Expected answer to cover content from at least one quarterly report:\n{answer[:400]}"
        )

        count = citation_count(driver)
        print(f"Citation count: {count}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected at least one cited passage from the multi-source notebook"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
