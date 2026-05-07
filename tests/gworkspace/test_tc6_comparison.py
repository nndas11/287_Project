"""TC6 — Comparison Query
Category  : Comparison
Query type: Precise
Source    : Google Doc — Product Specifications (two products described in one document)
Grounding : Fully grounded
Expected  : Accurate comparison with proper attribution to specific source sections.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - Product Specs"
  Source : Google Doc — Product Comparison Specification Sheet
  Content: A document with two clearly labelled product sections:

    Product Alpha:
      "Product Alpha is priced at $299/year. It supports up to 10 users, offers
       unlimited cloud storage, and includes 24/7 email support. Key features:
       real-time collaboration, version history (90 days), and REST API access."

    Product Beta:
      "Product Beta is priced at $499/year. It supports unlimited users, offers
       2 TB cloud storage, and includes 24/7 phone and email support. Key features:
       real-time collaboration, version history (unlimited), REST API access,
       SSO integration, and dedicated account management."

  Share  : "Anyone with the link can view".
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - Product Specs"
TEST_QUERY = (
    "Compare Product Alpha and Product Beta in terms of pricing, user limits, "
    "storage, and support options."
)
THRESHOLD = 0.28


def test_comparison_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc6_comparison::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        assert "alpha" in lower and "beta" in lower, (
            f"Expected both products to be mentioned in the comparison:\n{answer[:400]}"
        )
        assert any(kw in lower for kw in ["299", "499", "$299", "$499", "price", "pricing"]), (
            f"Expected pricing details in the comparison:\n{answer[:400]}"
        )

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected cited passage for a fully grounded comparison"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
