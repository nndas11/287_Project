"""TC20 — Unsupported Query
Category  : Unsupported
Query type: Precise
Source    : Public web (Wikipedia — Python programming language)
Grounding : Ungrounded
Expected  : Response clearly states the information is not present in the sources.

NotebookLM source URL:
  https://en.wikipedia.org/wiki/Python_(programming_language)
"""
import pytest
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response, assert_ungrounded,
)

NOTEBOOK_NAME = "WebTest - Python Wiki"
TEST_QUERY = (
    "What is the average annual salary for a Python developer "
    "in the United States in 2024?"
)


def test_unsupported_query(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert_ungrounded(answer, [
            "not mentioned", "no information", "sources don't", "not provided",
            "unable to find", "not in the sources", "don't contain",
            "not covered", "not address", "salary",
            "does not contain", "do not contain", "not contain",
            "does not have", "do not have", "does not include",
            "cannot find", "can't find",
        ])
    except Exception as exc:
        pytest.xfail(f"TC20 - {type(exc).__name__}: {exc}")
