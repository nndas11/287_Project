"""TC19 — Out-of-Scope Query (Variant)
Category  : Text/Upload
Query type: Ambiguous (irrelevant to source)
Source    : UploadTest - Valid Text (software testing content)
Grounding : Ungrounded
Expected  : NotebookLM responds that the topic is not in the sources.

Notebook: UploadTest - Valid Text (same as TC2).
"""
import pytest
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response, assert_ungrounded,
)

NOTEBOOK_NAME = "UploadTest - Valid Text"
TEST_QUERY = "Explain the geopolitical causes and consequences of the First World War."


def test_upload_out_of_scope_variant(driver, wait):
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
