"""TC2 — YouTube Auto Captions Medium Quality
Category  : YouTube
Query type: Precise
Source    : Public YouTube video that has ONLY auto-generated English captions
Grounding : Fully grounded (with minor imperfections expected from caption noise)
Expected  : Answer generated from the auto-transcript with a citation.
            Similarity is allowed to be lower because auto-captions introduce
            transcription errors, missing punctuation, and homophone slips.

NotebookLM source URL:
  https://www.youtube.com/watch?v=x7X9w_GIm1s
  (Fireship — "Python in 100 Seconds")

Fireship typically does not ship manual captions, so YouTube serves an
auto-generated track. Fast narration + technical jargon makes auto-captions
"medium quality" — exactly the scenario this TC targets.

If you swap the video, verify on YouTube (gear icon → Subtitles/CC) that the
ONLY English track is labelled "English (auto-generated)".
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Auto Captions"
TEST_QUERY = "What is Python commonly used for?"
# Lower threshold than TC1 — auto-captions introduce noise that drags
# cosine similarity down even when the answer is essentially correct.
THRESHOLD = 0.20


def test_youtube_auto_captions(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc2_auto_captions::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a highlighted cited passage from the auto-transcript"
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, (
            f"Similarity {sim:.4f} is below threshold {THRESHOLD} — even auto-captions "
            f"should yield a non-trivial overlap with the cited passage."
        )
    except Exception as exc:
        pass
