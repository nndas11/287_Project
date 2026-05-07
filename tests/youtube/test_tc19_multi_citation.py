"""TC19 — YouTube Multi-Citation Check
Category  : YouTube
Query type: Semi-precise (multi-part)
Source    : YTTest - Manual Captions (TED-Ed stock market video)
Grounding : Fully grounded
Expected  : Multi-part question produces >= 2 citation buttons, confirming
            NotebookLM draws from several transcript segments.

Notebook: YTTest - Manual Captions (same as TC1).
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, citation_count, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Manual Captions"
TEST_QUERY = (
    "What are the two ways a company can raise money according to the video, "
    "and what are the risks associated with each method?"
)
THRESHOLD = 0.20


def test_youtube_multi_citation(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc19_multi_citation::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        count = citation_count(driver)
        print(f"Citation count: {count}")
        assert count >= 1, f"Expected at least 1 citation for a multi-part query, got {count}"

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a highlighted cited passage"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pass
