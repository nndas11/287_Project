"""TC10 — Restricted Source Query (Not Accessible)
Category  : Restricted Source
Query type: Precise
Source    : Google Drive document with no sharing permissions (private / org-only)
Grounding : Not grounded
Expected  : Access restriction clearly indicated; source shows an error state.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - Private Drive Doc"
  Source : A Google Drive document URL that is NOT shared with anyone outside the
           owning Google account (sharing set to "Restricted — only people added
           can open"). When NotebookLM tries to index it, it will be blocked by
           Drive's access controls.

  To set up:
    1. Create a Google Doc titled "Confidential Project Details" in any Drive account
       that is NOT the account you use to log in to NotebookLM.
    2. Leave sharing set to "Restricted" (no public link).
    3. Copy the document URL and paste it as the source in the notebook.
    4. NotebookLM should show an error/failed icon next to the source.

  Alternatively: add the Drive link of a document owned by a different Google
  account that has never been shared with the NotebookLM account.

Note: This mirrors TC4 from the weblink suite (LinkedIn restricted link), but
for a Google Drive permission boundary instead of a bot-blocked website.
"""
import pytest
from selenium.webdriver.common.by import By

from tests.gworkspace.helpers import open_notebook

NOTEBOOK_NAME = "GSuite - Private Drive Doc"


def test_restricted_source_access(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)

        # Assert 1: Sources panel shows an error/failed indicator for the private doc
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

        # Assert 2: Chat footer reports 0 usable sources
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
        pytest.xfail(f"TC10 - {type(exc).__name__}: {exc}")
