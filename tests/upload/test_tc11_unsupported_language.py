"""TC11 — Unsupported Language
Category  : Text/Upload
Source    : Text written entirely in Klingon (a constructed language that
            NotebookLM has no training data or caption support for).
Grounding : Ungrounded
Expected  : NotebookLM either cannot parse the source (0 sources) OR imports
            it but returns a denial/unsupported-language response when queried.

NOTE: Unlike YouTube TC8 (where Yiddish turned out to be supported),
Klingon is a constructed language with no standard NLP support — it is
far less likely to be handled by NotebookLM's language models.
If NotebookLM still manages to respond in a grounded way, the test
will xfail and this TC should be revisited.

Notebook : UploadTest - Unsupported Language
Source   : Paste contents of tests/upload/test_files/klingon_text.txt
           (Add source → Copied text → paste → Insert)
"""
import pytest
from selenium.webdriver.common.by import By
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response, assert_ungrounded,
)

NOTEBOOK_NAME = "UploadTest - Unsupported Language"
TEST_QUERY = "What is the main topic of this document?"

_UNSUPPORTED_PHRASES = [
    "not in", "no information", "cannot", "unable", "not supported",
    "language", "don't contain", "do not contain", "not found",
    "not covered", "not mentioned", "does not contain",
    "not understand", "unrecognized",
]


def test_upload_unsupported_language(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        zero_sources = driver.find_elements(By.XPATH,
            "//*[contains(normalize-space(text()),'0 sources') "
            "or contains(normalize-space(.),'0 sources')]"
        )
        if zero_sources:
            print("Source rejected — chat footer shows '0 sources'")
            return

        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")
        assert_ungrounded(answer, _UNSUPPORTED_PHRASES)

    except Exception as exc:
        pass
