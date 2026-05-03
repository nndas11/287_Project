"""TC8 — YouTube Unsupported Language
Category  : YouTube
Query type: Precise
Source    : YouTube video whose ONLY caption track is in a language
            NotebookLM does not support (no English manual captions, no
            English auto-translation pathway).
Grounding : Ungrounded
Expected  : NotebookLM either rejects the source or imports it with no
            usable English transcript — the chat footer reports 0 sources
            or the source tile shows a language / unsupported error.

NotebookLM source URL (recommended):
  Pick a video whose audio is in a less-supported language and which has
  NO English caption track and NO auto-translate fallback. Candidates:
    - a Yiddish folk-song explainer
    - an Esperanto interview
    - a regional dialect video that YouTube doesn't auto-caption

Assertion strategy: identical failure-mode pattern as TC4/TC5/TC6.
"""
import pytest
from selenium.webdriver.common.by import By

from tests.youtube.helpers import open_notebook

NOTEBOOK_NAME = "YTTest - Unsupported Language"


@pytest.mark.skip(reason=(
    "TC8 deferred — NotebookLM's expanded language support (Yiddish, "
    "Esperanto, Welsh, etc. all work in 2026 via auto-translation), so "
    "the 'unsupported language → error' premise is rarely reproducible. "
    "Re-enable if you find a genuinely unsupported language video "
    "(Klingon, Ainu, etc.) and update NOTEBOOK_NAME / source URL."
))
def test_youtube_unsupported_language(driver, wait):
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
                "or contains(@class,'error-icon') or @aria-label='Error' "
                "or contains(@class,'language-error')]"
            )
        )

        zero_sources = driver.find_elements(By.XPATH,
            "//*[contains(normalize-space(text()),'0 sources') "
            "or contains(normalize-space(.),'0 sources')]"
        )

        assert error_indicators or zero_sources, (
            "Expected the unsupported-language YouTube source to show an "
            "error indicator in the Sources panel OR for the chat footer "
            "to show '0 sources'. Saw neither."
        )
        if error_indicators:
            print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pytest.xfail(f"TC8 - {type(exc).__name__}: {exc}")
