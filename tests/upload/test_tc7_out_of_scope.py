"""TC7 — Out-of-Scope Query
Category  : Text/Upload
Query type: Ambiguous (irrelevant to source)
Source    : REUSES UploadTest - Valid Text (software testing content)
Grounding : Ungrounded
Expected  : NotebookLM responds that the topic is not covered in the sources.

Notebook: UploadTest - Valid Text (same as TC2 — no new notebook needed).
"""
import pytest
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response, assert_ungrounded,
)

NOTEBOOK_NAME = "UploadTest - Valid Text"
TEST_QUERY = "What is the best recipe for making homemade sourdough bread from scratch?"


def test_upload_out_of_scope(driver, wait):
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
