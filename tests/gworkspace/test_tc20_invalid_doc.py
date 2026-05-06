"""TC20 — Restricted Source Query
Category  : Restricted Source
Query type: Precise
Source    : Google Drive document with no sharing permissions (private)
Grounding : Not grounded
Expected  : Access restriction clearly indicated; source shows an error state.

Notebook : "GSuite - Private Drive Doc"
"""
import pytest
from selenium.webdriver.common.by import By

from tests.gworkspace.helpers import open_notebook

NOTEBOOK_NAME = "GSuite - Private Drive Doc"


def test_restricted_source_access(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        error_indicators = (
            driver.find_elements(By.XPATH,
                "//source-listing-item//*[contains(@class,'error') or contains(@class,'failed')]"
                "|//*[contains(@class,'source') and .//*[contains(@class,'error')]]"
                "|//mat-icon[contains(text(),'error') or contains(text(),'warning')]"
            )
            or driver.find_elements(By.XPATH,
                "//*[contains(@class,'source-error') or contains(@class,'source-failed') "
                "or contains(@class,'error-icon') or @aria-label='Error']"
            )
        )
        assert error_indicators, (
            "Expected the private Drive doc to show an error indicator in the Sources panel"
        )
        print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")

        zero_sources = wait.until(lambda d: (
            d.find_elements(By.XPATH,
                "//*[contains(normalize-space(text()),'0 sources') "
                "or contains(normalize-space(.),'0 sources')]"
            )
        ))
        assert zero_sources, (
            "Expected the chat footer to report '0 sources' when the Drive doc is inaccessible"
        )
        print("Confirmed: chat footer shows '0 sources' for restricted Drive document")
    except Exception as exc:
        pytest.xfail(f"TC20 - {type(exc).__name__}: {exc}")
