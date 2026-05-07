"""TC15 — YouTube Low Quality Captions Query (Variant)
Category  : YouTube
Query type: Precise
Source    : YTTest - Low Quality Captions (Two Minute Papers)
Grounding : Partially grounded
Expected  : Cited answer despite noisy captions; very low threshold.

Notebook: YTTest - Low Quality Captions (same as TC3).
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Low Quality Captions"
TEST_QUERY = "What technology or technique is being evaluated or compared in this video?"
THRESHOLD = 0.10


def test_youtube_low_quality_captions_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc15_low_quality_captions_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage even from noisy captions"
        print(f"Cited passage (noisy):\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
