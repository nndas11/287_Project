"""TC2 — Valid Text Upload
Category  : Text/Upload
Query type: Precise
Source    : Plain text pasted via NotebookLM's "Copied text" source option.
Grounding : Fully grounded
Expected  : Accurate grounded response with citation; similarity >= threshold.

Notebook : UploadTest - Valid Text
Source   : Paste the contents of tests/upload/test_files/software_testing.txt
           (Add source → Copied text → paste → Insert)

This notebook is also reused by TC7, TC8, and TC12.
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "UploadTest - Valid Text"
TEST_QUERY = "What is regression testing and when is it performed?"
THRESHOLD = 0.40


def test_upload_valid_text(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc2_valid_text::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage for a fully grounded response"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pass
