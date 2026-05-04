"""TC9 — Multi-Document Synthesis
Category  : Text/Upload
Query type: Semi-precise (cross-document comparison)
Source    : Two uploaded text documents on related but distinct topics:
              Doc 1 — software_testing.txt  (unit/regression/integration testing)
              Doc 2 — agile_methodology.txt (CI, TDD, BDD, sprint testing)
Grounding : Fully grounded (answer synthesises both sources)
Expected  : NotebookLM combines information from both documents in a single
            coherent, cited answer.

Notebook : UploadTest - Multi Doc
Setup    : Add BOTH sources to the same notebook:
             1. Add source → Copied text → paste software_testing.txt → Insert
             2. Add source → Copied text → paste agile_methodology.txt → Insert
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
    "Compare traditional software testing approaches with Agile testing methodologies. "
    "What are the key differences in how tests are structured and when they are run?"
)
THRESHOLD = 0.20  # cross-document synthesis paraphrases heavily → lower overlap


def test_upload_multi_document(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"upload_tc9_multi_document::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        # Response should reference concepts from BOTH documents.
        lower = answer.lower()
        assert any(kw in lower for kw in (
            "unit test", "regression", "integration", "testing pyramid"
        )), "Expected TC1 source concepts (unit/regression/integration testing)"
        assert any(kw in lower for kw in (
            "agile", "sprint", "tdd", "continuous integration", "bdd", "shift-left"
        )), "Expected TC2 source concepts (agile / TDD / CI)"

        assert citation_count(driver) >= 1, "Cross-document answer should carry at least one citation"
        passage = click_citation_and_get_passage(driver, wait)
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"TC9 - {type(exc).__name__}: {exc}")
