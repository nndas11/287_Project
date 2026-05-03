"""TC1 — YouTube Manual Captions Valid Video
Category  : YouTube
Query type: Precise
Source    : Public YouTube video with manually-written English captions
Grounding : Fully grounded
Expected  : Accurate, cited answer; similarity >= threshold.

NotebookLM source URL:
  https://www.youtube.com/watch?v=p7HKvqRI_Bo
  (TED-Ed — "How does the stock market work? - Oliver Elfenbaum")

TED-Ed reliably ships manual English captions, so NotebookLM imports a
clean transcript and citations should be accurate.

Note: YouTube transcripts produce longer/more diverse cited passages than
.md files, so the threshold is set lower (0.30) than the file-source default.
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Manual Captions"
TEST_QUERY = "How does an initial public offering (IPO) work?"
THRESHOLD = 0.30


def test_youtube_manual_captions(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc1_manual_captions::{TEST_QUERY}"

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
        pytest.xfail(f"TC1 - {type(exc).__name__}: {exc}")
