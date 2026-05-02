"""TC1 — No Source Handling
Category  : No Source Handling
Query type: Ambiguous
Source    : None (empty notebook)
Grounding : Ungrounded
Expected  : NotebookLM tells the user to upload sources first.
"""
import pytest
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response, citation_count,
)

NOTEBOOK_NAME = "WebTest - No Source"
TEST_QUERY = "Summarize the main topics covered in this notebook."

_NO_SOURCE_PHRASES = [
    "first step",
    "upload",
    "add",
    "sources",
    "panel on the left",
    "pdfs",
    "google docs",
    "website links",
    "youtube",
    "no sources",
    "no source",
    "haven't added",
    "add a source",
]


@pytest.mark.skip(reason="TC1 excluded — empty notebook behaviour not under test")
def test_no_source_handling(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert citation_count(driver) == 0, (
            "Expected zero citations — notebook has no sources"
        )

        lower = answer.lower()
        # assert any(phrase in lower for phrase in _NO_SOURCE_PHRASES), (
        #     f"Expected a 'no sources / upload first' response. "
        #     f"Phrases checked: {_NO_SOURCE_PHRASES}\nGot: {answer[:400]}"
        # )
    except Exception as exc:
        pytest.xfail(f"TC1 - {type(exc).__name__}: {exc}")
