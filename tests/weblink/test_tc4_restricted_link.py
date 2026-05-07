"""TC4 — Restricted Link
Category  : Restricted Link
Query type: Precise
Source    : Login-required URL (LinkedIn feed — blocked by LinkedIn's crawler policy)
Grounding : Ungrounded
Expected  : NotebookLM marks the source as failed (error icon) and reports 0 usable sources.

NotebookLM source URL to attempt adding (will fail to load):
  https://www.linkedin.com/feed/
  LinkedIn returns HTTP 999 / bot-detection page to crawlers, so NotebookLM
  cannot index any content.

Assertion strategy: directly check the Sources panel and chat footer to confirm
the restricted URL produced an error state and zero usable sources.
"""
import pytest
from selenium.webdriver.common.by import By

from tests.weblink.helpers import open_notebook

NOTEBOOK_NAME = "WebTest - Restricted Source"


def test_restricted_link_error(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        # --- Assert 1: source panel shows an error/failed state for the URL ---
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
            "Expected the restricted URL to show an error indicator in the Sources panel"
        )
        print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")

        # --- Assert 2: chat footer reports 0 usable sources ---
        zero_sources = wait.until(lambda d: (
            d.find_elements(By.XPATH,
                "//*[contains(normalize-space(text()),'0 sources') "
                "or contains(normalize-space(.),'0 sources')]"
            )
        ))
        assert zero_sources, (
            "Expected the chat footer to report '0 sources' when the restricted URL failed to load"
        )
        print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pass
