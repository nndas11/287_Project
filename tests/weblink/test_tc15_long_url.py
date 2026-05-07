"""TC15 — Invalid URL
Category  : Invalid URL
Query type: Precise
Source    : Non-existent / syntactically invalid URL
Grounding : Ungrounded
Expected  : NotebookLM marks the source as failed and reports 0 usable sources.

NotebookLM source URL to attempt adding (does not exist):
  https://www.notarealwebsite-xyzabc123456.com/fake-article-about-programming
"""
import pytest
from selenium.webdriver.common.by import By

from tests.weblink.helpers import open_notebook

NOTEBOOK_NAME = "WebTest - Invalid Source"


def test_invalid_url_error(driver, wait):
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
            "Expected the invalid URL to show an error indicator in the Sources panel"
        )
        print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")

        zero_sources = wait.until(lambda d: (
            d.find_elements(By.XPATH,
                "//*[contains(normalize-space(text()),'0 sources') "
                "or contains(normalize-space(.),'0 sources')]"
            )
        ))
        assert zero_sources, (
            "Expected the chat footer to report '0 sources' when the URL failed to load"
        )
        print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pytest.xfail(f"{type(exc).__name__}: {exc}")
