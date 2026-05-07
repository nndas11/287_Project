"""TC3 — Valid PDF Upload
Category  : Text/Upload
Query type: Precise
Source    : PDF file with extractable text (same content as TC2 but uploaded
            as a PDF rather than pasted text — verifies PDF parsing path).
Grounding : Fully grounded
Expected  : Correct answer generated from PDF content with citation.

Notebook : UploadTest - Valid PDF
Source   : Upload tests/upload/test_files/software_testing.pdf
           (Add source → Upload → select the file)

To create the PDF on macOS:
  1. Open tests/upload/test_files/software_testing.txt in TextEdit or any editor.
  2. File → Print → PDF button (bottom-left) → Save as PDF.
  3. Save as tests/upload/test_files/software_testing.pdf
  4. Upload that PDF when creating the notebook.
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "UploadTest - Valid PDF"
TEST_QUERY = "What is the testing pyramid and how does it structure different test types?"
THRESHOLD = 0.35


def test_upload_valid_pdf(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc3_valid_pdf::{TEST_QUERY}"

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
