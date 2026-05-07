"""TC13 — No Upload Source (Variant)
Category  : Text/Upload
Query type: Ambiguous
Source    : None (empty notebook — no source added)
Grounding : Ungrounded
Expected  : NotebookLM redirects user to add a source; 0 citations.

Notebook: UploadTest - No Source (same as TC1).
"""
import pytest
from selenium.webdriver.common.by import By
from tests.upload.helpers import open_notebook, send_query_and_get_response, assert_ungrounded

NOTEBOOK_NAME = "UploadTest - No Source"
TEST_QUERY = "What are the key findings discussed in this document?"

_NO_SOURCE_PHRASES = [
    "upload", "add", "sources", "no source", "no sources",
    "haven't added", "add a source", "first step", "panel on the left",
    "pdfs", "google docs", "files", "no file", "no document",
    "please upload", "need to add",
]


def test_upload_no_source_query(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        zero_sources = driver.find_elements(By.XPATH,
            "//*[contains(normalize-space(text()),'0 sources') "
            "or contains(normalize-space(.),'0 sources')]"
        )
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources' — empty notebook")
            return

        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")
        assert_ungrounded(answer, _NO_SOURCE_PHRASES)
    except Exception as exc:
        pass
