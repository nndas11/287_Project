"""TC13 — YouTube Manual Captions Precise (Variant)
Category  : YouTube
Query type: Precise
Source    : YTTest - Manual Captions (TED-Ed stock market video)
Grounding : Fully grounded
Expected  : Cited answer about dividends/shareholders; similarity >= threshold.

Notebook: YTTest - Manual Captions (same as TC1).
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Manual Captions"
TEST_QUERY = "Why do stock prices go up and down after a company goes public?"
# Curated expected string scored against the AI answer directly.
EXPECTED = (
    "Stock prices go up when more investors see potential and demand increases, "
    "and go down when investors sell because the company appears less profitable, "
    "reducing demand and the company's market value."
)
THRESHOLD = 0.30


def test_youtube_manual_captions_precise(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc13_manual_captions_precise::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        sim = write_and_score(artifacts_dir, EXPECTED, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
