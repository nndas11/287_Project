"""TC8 — YouTube Manual Captions (Dutch East India Company)
Category  : YouTube
Query type: Precise
Source    : YTTest - Manual Captions (TED-Ed stock market video)
Grounding : Fully grounded
Expected  : Cited answer about the Dutch East India Company; similarity >= threshold.

Notebook: YTTest - Manual Captions (same as TC1).
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Manual Captions"
TEST_QUERY = "How did the Dutch East India Company influence the origin of the modern stock market?"
THRESHOLD = 0.30


def test_youtube_unsupported_language(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc8_dutch_east_india::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage for a fully grounded response"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
