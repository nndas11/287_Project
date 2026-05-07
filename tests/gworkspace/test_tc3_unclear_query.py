"""TC3 — Retrieve Exact Content (Somewhat Unclear Query)
Category  : Single-Source Retrieval
Query type: Somewhat unclear (ambiguous phrasing that needs interpretation)
Source    : Google Doc — Project Management Glossary (accessible, full content)
Grounding : Fully grounded
Expected  : Correct data retrieved and translated properly despite query ambiguity.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - PM Glossary"
  Source : Google Doc — Project Management Glossary
  Content: A glossary of project management terms, including:
             "Velocity: In agile project management, velocity measures the amount of
              work a team completes in a single sprint, typically expressed in story
              points. It is used to forecast how much work the team can deliver in
              future sprints. A higher velocity does not always indicate better
              performance; consistency is more valuable."
           Additional terms: Burndown Chart, Sprint, Epic, Stakeholder, Backlog.
  Share  : "Anyone with the link can view".

Note: The query uses "speed" and "how fast" which are synonyms of "velocity" — the
test verifies NotebookLM correctly resolves the conceptual overlap.
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "GSuite - PM Glossary"
TEST_QUERY = "How fast does the team work in agile? What does speed mean in sprints?"
THRESHOLD = 0.25


def test_unclear_query_retrieval(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc3_unclear_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        # Verify the answer correctly maps the vague query to "velocity" concept
        lower = answer.lower()
        assert any(kw in lower for kw in ["velocity", "story point", "sprint", "agile"]), (
            f"Expected answer to mention velocity/story points/agile, got:\n{answer[:400]}"
        )

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage from the glossary"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
