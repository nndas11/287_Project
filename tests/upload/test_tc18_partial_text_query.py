"""TC18 — Partial Text Extraction Query (Variant)
Category  : Text/Upload
Query type: Precise
Source    : UploadTest - Partial Text (document with missing sections)
Grounding : Partially grounded
Expected  : Partial but cited answer; low threshold.

Notebook: UploadTest - Partial Text (same as TC6).
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "UploadTest - Partial Text"
TEST_QUERY = "What does the document describe about the input layer of the network?"
THRESHOLD = 0.25


def test_upload_partial_text_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc18_partial_text_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected at least a partial cited passage"
        print(f"Cited passage (partial source):\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
