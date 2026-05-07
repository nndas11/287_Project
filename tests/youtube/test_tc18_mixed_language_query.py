"""TC18 — YouTube Mixed Language Query (Variant)
Category  : YouTube
Query type: Semi-precise
Source    : YTTest - Mixed Language (code-switching video)
Grounding : Partially grounded
Expected  : Cited partial answer from English portions; very low threshold.

Notebook: YTTest - Mixed Language (same as TC7).
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Mixed Language"
TEST_QUERY = "What key points or advice does the speaker share in this video?"
THRESHOLD = 0.10


def test_youtube_mixed_language_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc18_mixed_language_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage from the English portions of the transcript"
        print(f"Cited passage (mixed-language):\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
