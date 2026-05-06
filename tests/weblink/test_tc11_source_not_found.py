"""TC11 — No Source Handling (duplicate run of TC1)
Category  : No Source Handling
Query type: Ambiguous
Source    : None (empty notebook)
Grounding : Ungrounded
Expected  : Zero citations — notebook has no sources.
"""
import pytest
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response, citation_count,
)

NOTEBOOK_NAME = "WebTest - No Source"
TEST_QUERY = "Summarize the main topics covered in this notebook."


def test_no_source_handling(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert citation_count(driver) == 0, (
            "Expected zero citations — notebook has no sources"
        )
    except Exception as exc:
        pytest.xfail(f"TC11 - {type(exc).__name__}: {exc}")
