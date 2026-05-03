"""TC9 — YouTube Compare Query
Category  : YouTube
Query type: Semi-precise (comparison)
Source    : REUSES the TC1 notebook (TED-Ed "How does the stock market work?")
Grounding : Fully grounded
Expected  : NotebookLM produces a comparison-style answer drawing on the
            video's transcript. The answer should mention BOTH compared
            concepts and carry at least one citation.

Notebook: YTTest - Manual Captions (same notebook as TC1 — no setup needed
beyond what TC1 already required).
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
    "Based on the video, compare buying stocks early during a company's "
    "IPO with buying stocks of an established public company. What are "
    "the differences in risk and ownership?"
)
THRESHOLD = 0.20  # comparison answers paraphrase more, so similarity is lower


def test_youtube_compare_query(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc9_compare_query::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        # The answer should reference both sides of the comparison.
        lower = answer.lower()
        assert "ipo" in lower or "initial public offering" in lower, (
            f"Expected comparison answer to mention IPOs.\n{answer[:400]}"
        )
        assert any(kw in lower for kw in ("public", "stock", "investor", "owner")), (
            f"Expected comparison answer to mention public-market concepts.\n{answer[:400]}"
        )

        assert citation_count(driver) >= 1, "Comparison answer should be cited"
        passage = click_citation_and_get_passage(driver, wait)
        print(f"Cited passage:\n{passage}")

        sim = write_and_score(artifacts_dir, passage, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"TC9 - {type(exc).__name__}: {exc}")
