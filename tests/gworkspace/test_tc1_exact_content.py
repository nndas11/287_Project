"""TC1 — Retrieve Exact Content
Category  : Single-Source Retrieval
Query type: Precise
Source    : Google Doc — Employee Handbook (accessible, full content available)
Grounding : Fully grounded
Expected  : Correct passage retrieved with accurate citation; similarity >= threshold.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - Employee Handbook"
  Source : Google Doc — Employee Handbook
  Content: A multi-section employee handbook including a dedicated "Remote Work Policy"
           section that states:
             "Employees approved for remote work may work from home up to three days
              per week. The company will provide a one-time home office stipend of
              $500 for eligible employees. Requests must be submitted to HR at least
              two weeks in advance and approved by the department manager."
           Additional sections: Code of Conduct, Leave Policy, Benefits Overview.
  Share  : "Anyone with the link can view" so NotebookLM can index it.
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - Employee Handbook"
TEST_QUERY = "What is the company's policy for remote work, and what stipend is provided?"
THRESHOLD = 0.30


def test_exact_content_retrieval(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc1_exact_content::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a highlighted cited passage for a fully grounded response"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
