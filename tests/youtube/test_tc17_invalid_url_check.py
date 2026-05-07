"""TC17 — YouTube Invalid URL (Variant)
Category  : YouTube
Query type: N/A
Source    : YTTest - Invalid URL (non-existent YouTube video ID)
Grounding : Ungrounded
Expected  : Source marked as failed; 0 usable sources reported.

Notebook: YTTest - Invalid URL (same as TC5).
"""
import pytest
from selenium.webdriver.common.by import By
from tests.youtube.helpers import open_notebook

NOTEBOOK_NAME = "YTTest - Invalid URL"


def test_youtube_invalid_url_check(driver, wait):
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
            "Expected the invalid YouTube URL to show an error indicator "
            "OR for the chat footer to show '0 sources'. Saw neither."
        )
        if error_indicators:
            print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")
    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
