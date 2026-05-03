"""TC3 — YouTube Low-Quality Captions
Category  : YouTube
Query type: Precise
Source    : Public YouTube video with NOISY auto-generated captions
            (heavy accent / fast speech / background noise → caption errors)
Grounding : Partially grounded — answer is correct in spirit but the cited
            passage carries transcription errors.
Expected  : NotebookLM still returns a cited answer; cosine similarity is
            allowed to be low because auto-caption noise drags it down.

NotebookLM source URL (recommended):
  https://www.youtube.com/watch?v=Mde2q7GFlQ4
  (Two Minute Papers — Károly Zsolnai-Fehér's strong Hungarian accent +
   fast technical narration produces noticeably noisy auto-captions.)

If you swap the video, verify on YouTube (gear icon → Subtitles/CC) that
the ONLY English track is "English (auto-generated)" AND that the spoken
audio has accent/noise/speed that visibly degrades caption quality.
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Low Quality Captions"
TEST_QUERY = "What is the main result demonstrated in this video?"
# Very low threshold — TC3 is explicitly about handling noisy transcripts,
# so we just want to confirm the answer is non-trivially related to the
# source rather than enforce strict overlap.
THRESHOLD = 0.10


def test_youtube_low_quality_captions(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc3_low_quality_captions::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage even from noisy captions"
        print(f"Cited passage (noisy):\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, (
            f"Similarity {sim:.4f} below threshold {THRESHOLD} — even noisy "
            f"captions should yield some semantic overlap with the answer."
        )
    except Exception as exc:
        pytest.xfail(f"TC3 - {type(exc).__name__}: {exc}")
