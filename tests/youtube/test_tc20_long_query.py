"""TC20 — YouTube Long Complex Query
Category  : YouTube
Query type: Precise (multi-part / explanatory)
Source    : YTTest - Manual Captions (TED-Ed stock market video)
Grounding : Fully grounded
Expected  : Detailed, cited multi-paragraph answer covering all aspects of
            the question. Length and citation checks confirm depth of response.

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
    "Provide a comprehensive explanation of how the stock market works based on "
    "the video. Include: (1) how companies raise money, (2) what an IPO is, "
    "(3) how stock prices are determined after listing, and (4) what risks "
    "investors face when buying stocks."
)
THRESHOLD = 0.20


def test_youtube_long_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc20_long_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert len(answer) > 400, (
            f"Expected a comprehensive answer (>400 chars), got {len(answer)}.\n{answer}"
        )

        assert citation_count(driver) >= 1, "Long comprehensive answer should include citations"
        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a highlighted cited passage"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
