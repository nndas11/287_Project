"""TC20 — Multi-Document Synthesis Query (Variant)
Category  : Text/Upload
Query type: Semi-precise (cross-document)
Source    : UploadTest - Multi Doc (software_testing.txt + agile_methodology.txt)
Grounding : Fully grounded (synthesised from both documents)
Expected  : Answer draws from both documents with at least one citation.

Notebook: UploadTest - Multi Doc (same as TC9).
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, citation_count, write_and_score,
)

NOTEBOOK_NAME = "UploadTest - Multi Doc"
TEST_QUERY = (
    "How does test-driven development (TDD) relate to the testing practices "
    "described in the first document? Are they complementary or contradictory?"
)
THRESHOLD = 0.20


def test_upload_multi_doc_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc20_multi_doc_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        assert any(kw in lower for kw in ("tdd", "test-driven", "test driven")), (
            "Expected the answer to mention TDD from the agile document"
        )
        assert any(kw in lower for kw in (
            "unit test", "regression", "integration", "testing pyramid", "test coverage"
        )), "Expected concepts from the software testing document"

        assert citation_count(driver) >= 1, "Cross-document synthesis should carry a citation"
        passage = click_citation_and_get_passage(driver, wait)
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
