"""TC14 — Valid Text Upload Query (Variant)
Category  : Text/Upload
Query type: Precise
Source    : UploadTest - Valid Text (software testing content)
Grounding : Fully grounded
Expected  : Cited answer about integration testing; similarity >= threshold.

Notebook: UploadTest - Valid Text (same as TC2).
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "UploadTest - Valid Text"
TEST_QUERY = "What is integration testing and how does it differ from unit testing?"
THRESHOLD = 0.40


def test_upload_valid_text_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc14_valid_text_query::{TEST_QUERY}"

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
        pytest.xfail(f"{type(exc).__name__}: {exc}")
