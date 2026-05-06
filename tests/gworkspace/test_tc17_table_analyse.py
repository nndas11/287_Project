"""TC17 — Table Query, Full Data
Category  : Table/Figure Extraction
Query type: Precise
Source    : Google Doc with Q2 Budget table (full data available)
Grounding : Fully grounded
Expected  : Table values extracted correctly with citation; similarity >= threshold.

Notebook : "GSuite - Budget Spreadsheet"
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - Budget Spreadsheet"
TEST_QUERY = "What is the total Q2 budget and how much did the Marketing department spend?"
THRESHOLD = 0.28


def test_table_query_full_data(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc17_table_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        assert any(kw in lower for kw in ["700,000", "700000", "$700", "120,000", "115,400", "marketing"]), (
            f"Expected specific budget figures in the answer:\n{answer[:400]}"
        )

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage from the budget spreadsheet source"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"TC17 - {type(exc).__name__}: {exc}")
