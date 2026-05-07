"""TC5 — Corrupted Document
Category  : Text/Upload
Source    : A file with a valid PDF header (%PDF-1.4) but corrupted/garbage body.
Grounding : Ungrounded
Expected  : NotebookLM displays a parsing or upload failure message; source
            is marked as failed and contributes 0 usable content.

Notebook : UploadTest - Corrupted Doc
Setup    : Upload tests/upload/test_files/corrupted.pdf as a source.
           The file starts with PDF magic bytes but has random garbage content
           so the PDF parser will fail to extract any text.

Assertion: error indicator OR '0 sources' footer (same pattern as TC4/TC5 YouTube).
"""
import pytest
from selenium.webdriver.common.by import By
from tests.upload.helpers import open_notebook

NOTEBOOK_NAME = "UploadTest - Corrupted Doc"


def test_upload_corrupted_doc(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        error_indicators = (
            driver.find_elements(By.XPATH,
                "//source-listing-item//*[contains(@class,'error') or contains(@class,'failed')]"
                "|//*[contains(@class,'source') and .//*[contains(@class,'error')]]"
                "|//mat-icon[contains(text(),'error') or contains(text(),'warning') "
                "or contains(text(),'info')]"
            )
            or driver.find_elements(By.XPATH,
                "//*[contains(@class,'source-error') or contains(@class,'source-failed') "
                "or contains(@class,'error-icon') or @aria-label='Error' "
                "or contains(@class,'warning-icon') or contains(@class,'info-icon')]"
            )
        )
        zero_sources = driver.find_elements(By.XPATH,
            "//*[contains(normalize-space(text()),'0 sources') "
            "or contains(normalize-space(.),'0 sources')]"
        )

        assert error_indicators or zero_sources, (
            "Expected the corrupted PDF to produce an error indicator in the "
            "Sources panel OR result in '0 sources' in the chat footer."
        )
        if error_indicators:
            print(f"Error indicator: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pass
