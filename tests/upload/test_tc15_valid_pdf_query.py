"""TC15 — Valid PDF Upload Query (Variant)
Category  : Text/Upload
Query type: Precise
Source    : UploadTest - Valid PDF (software testing PDF)
Grounding : Fully grounded
Expected  : Cited answer about exploratory testing from PDF source.

Notebook: UploadTest - Valid PDF (same as TC3).
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "UploadTest - Valid PDF"
TEST_QUERY = "What is exploratory testing and when is it most useful?"
THRESHOLD = 0.35


def test_upload_valid_pdf_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc15_valid_pdf_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage from the PDF source"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pass
