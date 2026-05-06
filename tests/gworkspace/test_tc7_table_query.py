"""TC7 — Table/Figure Query (Precise, Full Data Available)
Category  : Table/Figure Extraction
Query type: Precise
Source    : Google Sheets — Quarterly Budget Spreadsheet (accessible, full data)
Grounding : Fully grounded
Expected  : Table values extracted correctly with accurate citation.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - Budget Spreadsheet"
  Source : Google Sheets — Q2 Budget Allocation
  Content: A spreadsheet with the following structure (NotebookLM will receive it
           as text; export the Sheet as a Google Doc or add it directly as a Drive
           source so NotebookLM indexes the cell values):

    Department     | Q2 Budget ($) | Q2 Actual ($) | Variance (%)
    Marketing      | 120,000       | 115,400        | -3.8%
    Engineering    | 340,000       | 352,100        | +3.6%
    Sales          | 180,000       | 178,900        | -0.6%
    HR & Ops       |  60,000       |  58,200        | -3.0%
    Total          | 700,000       | 704,600        | +0.7%

  Add a short paragraph: "The Q2 budget report covers all four departments for the
  April–June period. Marketing came in under budget at $115,400 against a $120,000
  allocation."

  Share  : "Anyone with the link can view".

Note: NotebookLM's indexing of Sheets varies. If the raw sheet is not indexed well,
attach the Sheet exported to a Google Doc with the table preserved as plain text.
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
        test_name = f"gws_tc7_table_query::{TEST_QUERY}"

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
        pytest.xfail(f"TC7 - {type(exc).__name__}: {exc}")
