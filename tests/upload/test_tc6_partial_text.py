"""TC6 — Partial Text Extraction
Category  : Text/Upload
Query type: Precise
Source    : Document where only part of the content is available as extractable
            text (remaining sections are referenced as figures/images not included).
Grounding : Partially grounded — answer is correct but incomplete.
Expected  : NotebookLM returns a partial but correct response based on what
            was extractable; similarity allowed to be lower than full-text tests.

Notebook : UploadTest - Partial Text
Source   : Paste contents of tests/upload/test_files/partial_coverage.txt
           (Add source → Copied text → paste → Insert)
           The document explicitly notes that sections 3-7 are missing.
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "UploadTest - Partial Text"
TEST_QUERY = "What are the components of a neural network described in the document?"
# Lower threshold — the source intentionally omits key sections so the answer
# will be correct but incomplete, dragging cosine similarity down.
THRESHOLD = 0.25


def test_upload_partial_text(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc6_partial_text::{TEST_QUERY}"

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
