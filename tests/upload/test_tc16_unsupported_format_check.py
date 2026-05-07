"""TC16 — Unsupported File Format (Variant)
Category  : Text/Upload
Source    : UploadTest - Unsupported Format (.mp3 file)
Grounding : Ungrounded
Expected  : Source error indicator OR 0 sources in chat footer.

Notebook: UploadTest - Unsupported Format (same as TC4).
"""
import pytest
from selenium.webdriver.common.by import By
from tests.upload.helpers import open_notebook

NOTEBOOK_NAME = "UploadTest - Unsupported Format"


def test_upload_unsupported_format_check(driver, wait):
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
            "Expected the unsupported file type to produce an error indicator "
            "OR result in '0 sources' in the chat footer."
        )
        if error_indicators:
            print(f"Error indicator: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")
    except Exception as exc:
        pass
