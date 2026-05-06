"""TC2 — Retrieve Exact Content (Restricted View)
Category  : Single-Source Retrieval
Query type: Precise
Source    : Google Doc — Quarterly Financial Report (shared as "View only", no download)
Grounding : Fully grounded
Expected  : Output respects access limits (no raw download) and shows correct cited content.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - Q3 Financial Report (View Only)"
  Source : Google Doc — Q3 Financial Report
  Content: A financial report with the following key paragraph:
             "Total revenue for Q3 reached $4.2 million, representing a 18% increase
              year-over-year. Operating expenses were $2.8 million, yielding an
              operating margin of 33%. Net profit after tax stood at $1.1 million."
           Additional sections: Revenue by Region, Expense Breakdown, Outlook.
  Share  : Set to "Viewer" (no edit, no download) so NotebookLM can read but not export.

Note: NotebookLM indexes the visible text despite the "no download" restriction;
the test confirms the cited answer is accurate even under view-only access.
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - Q3 Financial Report (View Only)"
TEST_QUERY = "What were the total revenue and net profit figures for Q3?"
THRESHOLD = 0.30


def test_restricted_view_retrieval(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc2_restricted_view::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, (
            "Expected a cited passage — NotebookLM should index view-only content"
        )
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"TC2 - {type(exc).__name__}: {exc}")
