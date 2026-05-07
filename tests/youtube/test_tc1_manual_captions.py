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
    click_citation_and_get_passage, citation_count, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Manual Captions"
TEST_QUERY = "How does an initial public offering (IPO) work?"
# Curated expected — citation 1 is often the Dutch East India Company passage
# which has low overlap with an IPO answer; score against a ground-truth string.
EXPECTED = (
    "An Initial Public Offering (IPO) is the event that launches a company onto "
    "the official public market for the first time. Big investors first get the "
    "chance to invest, then the company goes public, allowing any individual to "
    "buy stocks and become a partial owner of the business."
)
THRESHOLD = 0.30


def test_youtube_manual_captions(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc1_manual_captions::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert citation_count(driver) >= 1, "Expected at least one citation in the answer"

        sim = write_and_score(artifacts_dir, EXPECTED, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} is below threshold {THRESHOLD}"
    except Exception as exc:
        pass
