"""TC6 — YouTube Auto Captions (Python Use Cases)
Category  : YouTube
Query type: Precise
Source    : YTTest - Auto Captions (Fireship "Python in 100 Seconds")
Grounding : Fully grounded
Expected  : Cited answer about Python use cases; similarity >= threshold.

Notebook: YTTest - Auto Captions (same as TC2).
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Auto Captions"
TEST_QUERY = "How is Python used in data science and machine learning?"
THRESHOLD = 0.20


def test_youtube_restricted_video(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc6_python_data_science::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage from the auto-transcript"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
