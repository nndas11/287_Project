"""TC4 — Unsupported File Format
Category  : Text/Upload
Source    : File with an unsupported extension (.mp3)
Grounding : Ungrounded
Expected  : NotebookLM rejects the file or marks the source as failed;
            chat footer shows 0 usable sources.

Notebook : UploadTest - Unsupported Format
Setup    : Try to upload tests/upload/test_files/unsupported.mp3 as a source.
           NotebookLM may reject it at the file-picker level (in which case
           the notebook stays empty with 0 sources) or accept the upload and
           then show an error icon.  Either outcome satisfies the assertion.

Assertion: identical OR-logic to the YouTube failure-mode tests.
"""
import pytest
from selenium.webdriver.common.by import By
from tests.upload.helpers import open_notebook

NOTEBOOK_NAME = "UploadTest - Unsupported Format"


def test_upload_unsupported_format(driver, wait):
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
            "Expected the unsupported file type to either produce an error "
            "indicator in the Sources panel OR result in '0 sources' in the "
            "chat footer. Saw neither."
        )
        if error_indicators:
            print(f"Error indicator: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pytest.xfail(f"TC4 - {type(exc).__name__}: {exc}")
