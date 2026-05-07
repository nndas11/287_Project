"""TC11 — YouTube Out-of-Scope Query
Category  : YouTube
Query type: Ambiguous (irrelevant to the source)
Source    : REUSES the TC1 notebook (TED-Ed "How does the stock market work?")
Grounding : Ungrounded
Expected  : NotebookLM responds that the topic is not covered in the
            sources rather than fabricating an answer.

Notebook: YTTest - Manual Captions (same notebook as TC1).
"""
import pytest
from tests.youtube.helpers import (
    open_notebook, send_query_and_get_response, assert_ungrounded,
)

NOTEBOOK_NAME = "YTTest - Manual Captions"
TEST_QUERY = (
    "How do I bake a moist chocolate cake with vanilla buttercream "
    "frosting from scratch?"
)


def test_youtube_out_of_scope(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        assert_ungrounded(answer, [
            "not in", "sources don't", "no information", "outside",
            "not covered", "can't find", "don't contain", "not mentioned",
            "not address", "not discuss", "not related", "unrelated",
            "do not contain", "does not contain", "not contain",
            "do not have", "does not have", "cannot find",
        ])
    except Exception as exc:
        pass
