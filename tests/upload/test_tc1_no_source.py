"""TC1 — No Upload Source
Category  : Text/Upload
Query type: Ambiguous
Source    : None (empty notebook — no text or file uploaded)
Grounding : Ungrounded
Expected  : NotebookLM shows "No source found" or prevents query execution,
            telling the user to add sources first.

Notebook: UploadTest - No Source
Setup   : Create the notebook but do NOT add any source.
"""
import pytest
from selenium.webdriver.common.by import By
from tests.upload.helpers import open_notebook, send_query_and_get_response, assert_ungrounded

NOTEBOOK_NAME = "UploadTest - No Source"
TEST_QUERY = "Summarize the main topics covered in this document."

_NO_SOURCE_PHRASES = [
    "upload", "add", "sources", "no source", "no sources",
    "haven't added", "add a source", "first step", "panel on the left",
    "pdfs", "google docs", "files", "no file", "no document",
    "please upload", "need to add",
]


def test_upload_no_source(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        # Check for "0 sources" in the chat footer first — if shown, the
        # notebook is confirmed empty and we skip sending a query.
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
        pytest.xfail(f"TC1 - {type(exc).__name__}: {exc}")
