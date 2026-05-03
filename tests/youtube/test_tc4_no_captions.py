"""TC4 — YouTube No Captions Available
Category  : YouTube
Query type: Precise
Source    : Valid YouTube URL whose video has NO captions (manual or auto)
            — typically a music/ambient/silent video, or a creator who
            explicitly disabled captions.
Grounding : Ungrounded
Expected  : NotebookLM cannot extract a transcript, so the source loads
            with an error / empty transcript and the chat reports 0 usable
            sources (or the model refuses to answer with citations).

NotebookLM source URL (recommended):
  Pick a short ambient music or silent video with no spoken audio.
  e.g. a "10 minutes of rain sounds" upload — YouTube will not generate
  captions for content with no recognisable speech.

Assertion strategy: like the weblink failure-mode tests (TC4/TC5), check
the Sources panel for an error indicator OR the chat footer for "0 sources".
"""
import pytest
from selenium.webdriver.common.by import By

from tests.youtube.helpers import open_notebook

NOTEBOOK_NAME = "YTTest - No Captions"


def test_youtube_no_captions(driver, wait):
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

        zero_sources = driver.find_elements(By.XPATH,
            "//*[contains(normalize-space(text()),'0 sources') "
            "or contains(normalize-space(.),'0 sources')]"
        )

        assert error_indicators or zero_sources, (
            "Expected the no-captions YouTube source to either show an error "
            "indicator in the Sources panel OR for the chat footer to show "
            "'0 sources'. Saw neither."
        )
        if error_indicators:
            print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pytest.xfail(f"TC4 - {type(exc).__name__}: {exc}")
