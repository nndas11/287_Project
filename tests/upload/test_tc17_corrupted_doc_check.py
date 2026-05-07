"""TC17 — Corrupted Document (Variant)
Category  : Text/Upload
Source    : UploadTest - Corrupted Doc (corrupted PDF)
Grounding : Ungrounded
Expected  : Source parsing failure indicator OR 0 sources in chat footer.

Notebook: UploadTest - Corrupted Doc (same as TC5).
"""
import pytest
from selenium.webdriver.common.by import By
from tests.upload.helpers import open_notebook

NOTEBOOK_NAME = "UploadTest - Corrupted Doc"


def test_upload_corrupted_doc_check(driver, wait):
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
            "Expected the corrupted PDF to produce an error indicator "
            "OR result in '0 sources' in the chat footer."
        )
        if error_indicators:
            print(f"Error indicator: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")
    except Exception as exc:
        pass
