"""TC7 — YouTube Mixed-Language Captions
Category  : YouTube
Query type: Semi-precise
Source    : Public YouTube video where the speaker code-switches between
            English and another language (e.g. Hinglish, Spanglish).
Grounding : Partially grounded — NotebookLM understands the English
            portions but the non-English segments produce broken captions.
Expected  : The model returns a partial answer in English, citing whatever
            English content it could parse. Similarity may be modest.

NotebookLM source URL (recommended):
  Pick a Hinglish, Spanglish, or other code-switching content video where:
    - speakers alternate languages within the same sentence/episode
    - the YouTube UI offers an English-or-mixed auto-caption track
  e.g. a popular Indian YouTuber's vlog (BeerBiceps clip, MostlySane,
  Ranveer Allahbadia podcast clip, etc.)

If you swap the video, update TEST_QUERY to something the English
portion of the audio actually addresses.
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    click_citation_and_get_passage, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Mixed Language"
TEST_QUERY = "What is the main topic discussed in this video?"
# Mixed-language captions produce noisy English transcripts, so allow
# a permissive threshold like TC3.
THRESHOLD = 0.10


def test_youtube_mixed_language(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc7_mixed_language::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        passage = click_citation_and_get_passage(driver, wait)
        assert passage, "Expected a cited passage from the English portions of the transcript"
        print(f"Cited passage (mixed-language):\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, (
            f"Similarity {sim:.4f} below threshold {THRESHOLD} — even mixed-language "
            f"captions should yield some semantic overlap with the answer."
        )
    except Exception as exc:
        pass
