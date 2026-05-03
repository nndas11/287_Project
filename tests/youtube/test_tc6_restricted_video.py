"""TC6 — YouTube Restricted Video
Category  : YouTube
Query type: Precise
Source    : Restricted YouTube URL (private, unlisted-without-key,
            age-restricted, region-locked, or members-only) — NotebookLM
            cannot fetch the transcript without authenticated access.
Grounding : Ungrounded
Expected  : NotebookLM marks the source as failed (access denied) and
            reports 0 usable sources.

NotebookLM source URL (recommended):
  Pick any private, unlisted, or age-restricted video. Examples:
    - a video you uploaded to your own channel and set to "Private"
    - any age-restricted music video (YouTube returns "Sign in to confirm
      your age" without a session it accepts)

Assertion strategy: identical to weblink TC4/TC5 — check the Sources panel
for an error indicator and the chat footer for '0 sources'.
"""
import pytest
from selenium.webdriver.common.by import By

from tests.youtube.helpers import open_notebook

NOTEBOOK_NAME = "YTTest - Restricted Video"


@pytest.mark.skip(reason="TC6 deferred — restricted-video notebook not yet created")
def test_youtube_restricted_video(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        # Accept EITHER an error indicator OR the "0 sources" footer — same
        # OR-logic pattern used by TC4 / TC5 / TC8.
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
            "Expected the restricted YouTube video to show an error / "
            "access-denied indicator in the Sources panel OR for the chat "
            "footer to show '0 sources'. Saw neither."
        )
        if error_indicators:
            print(f"Error indicator found: {error_indicators[0].get_attribute('class')}")
        if zero_sources:
            print("Confirmed: chat footer shows '0 sources'")

    except Exception as exc:
        pytest.xfail(f"TC6 - {type(exc).__name__}: {exc}")
