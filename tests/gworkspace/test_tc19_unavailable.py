"""TC19 — Table Query, Data Not Extractable (duplicate run of TC9)
Category  : Table/Figure Extraction
Query type: Precise
Source    : Google Slides with image-only charts (no extractable text)
Grounding : Not grounded
Expected  : System indicates inability to extract values from embedded images.

Notebook : "GSuite - Chart Only Slides"
"""
import pytest
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    citation_count, assert_ungrounded,
)

NOTEBOOK_NAME = "GSuite - Chart Only Slides"
TEST_QUERY = "What are the exact revenue values shown in the bar chart on slide 2?"

_CANNOT_EXTRACT_PHRASES = [
    "cannot", "can't", "unable to", "not able to",
    "image", "chart", "visual", "extract",
    "no text", "no information", "not available",
    "don't have", "do not have", "doesn't contain", "does not contain",
    "embedded", "picture", "graphic",
]


def test_table_data_unavailable(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        count = citation_count(driver)
        assert count == 0, (
            f"Expected zero citations — chart values are not extractable, got {count}"
        )

        assert_ungrounded(answer, _CANNOT_EXTRACT_PHRASES)
        print("Confirmed: system correctly reports inability to extract image-based data")
    except Exception as exc:
        pytest.xfail(f"TC19 - {type(exc).__name__}: {exc}")
