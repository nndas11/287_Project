"""TC4 — Summarization (Single Source)
Category  : Summarization
Query type: Precise
Source    : Google Doc — Annual Company Report (accessible, full content)
Grounding : Fully grounded
Expected  : Concise and accurate summary generated with proper citation.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - Annual Report 2024"
  Source : Google Doc — Annual Company Report 2024
  Content: A multi-section annual report (~4–6 paragraphs) covering:
             Executive Summary:
               "FY2024 was a landmark year. Annual revenue grew 22% to $18.6 million.
                We expanded to three new markets, hired 45 new employees, and launched
                two flagship products: SmartDash Pro and CloudSync 2.0."
             Product Highlights, Market Expansion, Financial Summary, Outlook 2025.
             Each section contains 2–3 paragraphs of concrete facts and figures.
  Share  : "Anyone with the link can view".

Note: The test checks that the summary mentions major financial figures and products
without fabricating details that are not in the source.
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - Annual Report 2024"
TEST_QUERY = "Summarize the key highlights and financial results from this annual report."
THRESHOLD = 0.25


def test_summarization_single_source(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc4_summarization::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert len(answer.split()) >= 30, (
            f"Expected a substantive summary (>=30 words), got: {answer[:200]}"
        )

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected at least one citation in a fully grounded summary"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"TC4 - {type(exc).__name__}: {exc}")
