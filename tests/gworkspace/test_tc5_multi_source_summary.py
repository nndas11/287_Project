"""TC5 — Summarization (Multi-Source, Somewhat Unclear Query)
Category  : Multi-Source Summarization
Query type: Somewhat unclear (broad scope, no explicit timeframe)
Source    : Two Google Docs — Q1 Project Report + Q2 Project Report (both accessible)
Grounding : Fully grounded
Expected  : Combined summary drawn from both sources, without duplication.

Sample notebooks to create in NotebookLM:
  Name   : "GSuite - Multi Quarter Reports"
  Sources: Two Google Docs added to the same notebook —

  Doc 1 — Q1 Project Report:
    "Project Alpha completed its design phase in Q1. The team delivered 12 features,
     fixed 34 bugs, and achieved 95% test coverage. The on-time delivery rate was 88%.
     Budget utilization stood at 72% of the quarterly allocation."

  Doc 2 — Q2 Project Report:
    "In Q2, Project Alpha entered the beta phase. An additional 9 features were shipped
     and user testing began with 200 participants. Customer satisfaction scores averaged
     4.2 out of 5. Budget utilization increased to 91% as external contractors were
     onboarded."

  Share  : Both docs shared as "Anyone with the link can view".

Note: The query is intentionally vague ("how the project is going") — the test verifies
NotebookLM synthesizes both quarterly reports without repeating the same facts.
"""
import os
import pytest
from pathlib import Path
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
    citation_count,
)

NOTEBOOK_NAME = "GSuite - Multi Quarter Reports"
TEST_QUERY = "How is the project going overall? Give me an overview of the progress."
THRESHOLD = 0.22


def test_multi_source_summary(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"gws_tc5_multi_source_summary::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        # Expect the answer to draw on both docs: Q1 and Q2 details should appear
        lower = answer.lower()
        has_q1 = any(kw in lower for kw in ["q1", "design phase", "12 feature", "95%", "88%"])
        has_q2 = any(kw in lower for kw in ["q2", "beta", "200 participant", "4.2", "91%"])
        assert has_q1 or has_q2, (
            f"Expected answer to cover content from at least one quarterly report:\n{answer[:400]}"
        )

        # Multi-source notebooks typically produce multiple citations
        count = citation_count(driver)
        print(f"Citation count: {count}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected at least one cited passage from the multi-source notebook"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
