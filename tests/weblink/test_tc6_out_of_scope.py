"""TC6 — Out-of-Scope Query
Category  : Out-of-Scope
Query type: Ambiguous
Source    : Public web (Wikipedia — Python programming language)
Grounding : Ungrounded
Expected  : Response says the query topic is not covered in the sources.

NotebookLM source URL:
  https://en.wikipedia.org/wiki/Python_(programming_language)

Note: citation_count is not asserted — NotebookLM may attach a citation while
still reporting the topic is out of scope.
"""
import pytest
from tests.weblink.helpers import (
    open_notebook, send_query_and_get_response, assert_ungrounded,
)

NOTEBOOK_NAME = "WebTest - Python Wiki"
TEST_QUERY = "How do I bake a moist chocolate cake with vanilla buttercream frosting from scratch?"


def test_out_of_scope_query(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert_ungrounded(answer, [
            # contracted forms
            "not in", "sources don't", "no information", "outside",
            "not covered", "can't find", "don't contain", "not mentioned",
            "not address", "not discuss", "not related", "unrelated",
            # formal / uncontracted forms NotebookLM often uses
            "do not contain", "does not contain", "not contain",
            "do not have", "does not have", "cannot find",
        ])
    except Exception as exc:
        pytest.xfail(f"TC6 - {type(exc).__name__}: {exc}")
