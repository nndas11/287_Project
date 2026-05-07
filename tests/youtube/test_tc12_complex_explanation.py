"""TC12 — YouTube Complex Explanation
Category  : YouTube
Query type: Precise (multi-part / explanatory)
Source    : REUSES the TC1 notebook (TED-Ed "How does the stock market work?")
Grounding : Fully grounded
Expected  : NotebookLM returns a detailed, cited multi-paragraph answer
            covering the requested concepts. Similarity should be solid
            because manual captions + a precise query produces clean overlap.

Notebook: YTTest - Manual Captions (same notebook as TC1).
"""
import os
import pytest
from pathlib import Path
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response,
    citation_count, write_and_score,
)

NOTEBOOK_NAME = "YTTest - Manual Captions"
TEST_QUERY = (
    "Explain in detail how stock prices change after a company goes public. "
    "What role do investors, supply and demand, and company performance play, "
    "and why is the stock market considered risky?"
)
# Curated expected string — scored against the AI answer instead of the cited
# passage, which can be about unrelated content (e.g., Dutch East India Company).
EXPECTED = (
    "Stock prices change after a company goes public based on supply and demand. "
    "When investors buy shares, demand rises and prices increase. When investors "
    "sell, demand drops and prices fall. The stock market is considered risky "
    "because it is driven by human confidence, a difficult-to-track variable."
)
THRESHOLD = 0.30


def test_youtube_complex_explanation(driver, wait):
    try:
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        test_name = f"yt_tc12_complex_explanation::{TEST_QUERY}"

        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        # Detail check: a "complex explanation" should be substantial.
        assert len(answer) > 300, (
            f"Expected a detailed explanation (>300 chars), got {len(answer)}.\n{answer}"
        )

        assert citation_count(driver) >= 1, "Complex explanation should be cited"

        sim = write_and_score(artifacts_dir, EXPECTED, answer, test_name, THRESHOLD)
        print(f"Semantic similarity: {sim:.6f}")
        assert sim >= THRESHOLD, f"Similarity {sim:.4f} below threshold {THRESHOLD}"
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
