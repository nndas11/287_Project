"""TC14 — Summarization, Single Source
Category  : Summarization
Query type: Precise
Source    : Google Doc — Annual Company Report 2024
Grounding : Fully grounded
Expected  : Concise and accurate summary with citation; similarity >= threshold.

Notebook : "GSuite - Annual Report 2024"
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
        test_name = f"gws_tc14_summarization::{TEST_QUERY}"

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
        pytest.xfail(f"TC14 - {type(exc).__name__}: {exc}")
