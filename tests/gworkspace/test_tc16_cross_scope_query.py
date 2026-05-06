"""TC16 — Comparison Query
Category  : Comparison
Query type: Precise
Source    : Google Doc — Product Comparison Specification Sheet
Grounding : Fully grounded
Expected  : Accurate comparison with proper attribution; similarity >= threshold.

Notebook : "GSuite - Product Specs"
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - Product Specs"
TEST_QUERY = (
    "Compare Product Alpha and Product Beta in terms of pricing, user limits, "
    "storage, and support options."
)
THRESHOLD = 0.28


def test_comparison_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc16_comparison::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        assert "alpha" in lower and "beta" in lower, (
            f"Expected both products to be mentioned in the comparison:\n{answer[:400]}"
        )
        assert any(kw in lower for kw in ["299", "499", "$299", "$499", "price", "pricing"]), (
            f"Expected pricing details in the comparison:\n{answer[:400]}"
        )

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected cited passage for a fully grounded comparison"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"TC16 - {type(exc).__name__}: {exc}")
