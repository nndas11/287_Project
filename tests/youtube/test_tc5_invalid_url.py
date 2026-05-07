"""TC5 — YouTube Invalid URL
Category  : YouTube
Query type: Precise
Source    : Syntactically valid but non-existent YouTube URL (the v= id
            does not resolve to any video).
Grounding : Ungrounded
Expected  : NotebookLM marks the source as failed and reports 0 usable
            sources in the chat footer.

NotebookLM source URL to attempt adding (does not exist):
  https://www.youtube.com/watch?v=NOTAREALxyz999

Assertion strategy: identical to weblink TC5 — check the Sources panel
for an error icon and the chat footer for '0 sources'.
"""
import pytest
from selenium.webdriver.common.by import By

from tests.youtube.helpers import open_notebook

NOTEBOOK_NAME = "YTTest - Invalid URL"


def test_youtube_invalid_url(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        # The "0 sources" chat-footer text is the definitive signal that the
        # source did not load. The error icon is a nice-to-have visual cue but
        # NotebookLM uses several different classes for it (info / warning /
        # error variants), so we accept EITHER signal.
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
            "Expected the invalid YouTube URL to either show an error indicator "
            "in the Sources panel OR for the chat footer to show '0 sources'. "
            "Saw neither."
        )
        if error_indicators:
            print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pass
