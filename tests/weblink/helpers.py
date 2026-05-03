"""Shared Selenium helpers for web-link-source NotebookLM tests."""
import os
import time
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

NOTEBOOKLM_URL = "https://notebooklm.google.com/"

_SAVE_NOTE = (By.XPATH, "//span[text()='Save to note']")
_THINKING  = (By.XPATH, "//div[contains(@class,'thinking-animation-container')]")
_ANSWER    = (By.XPATH, "//mat-card-content[contains(@class,'to-user-message-inner-content')]")


def open_notebook(driver, wait, notebook_name: str) -> None:
    """Navigate to NotebookLM home and open the named notebook card."""
    driver.get(NOTEBOOKLM_URL)
    title_el = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        f"//span[contains(@class,'project-button-title') and "
        f"contains(normalize-space(.), '{notebook_name}')]",
    )))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", title_el)
    targets = [
        *title_el.find_elements(By.XPATH,
            "./ancestor::mat-card[contains(@class,'project-button-card')]"
            "|./ancestor::project-button"
            "|./ancestor::*[self::a or self::button or @role='button' "
            "or contains(@class,'primary-action-button')]"),
        title_el,
    ]
    clicked = False
    for t in targets:
        if t is None:
            continue
        try:
            # Capture t by value (default arg) so the lambda always refers to this
            # specific element, and guard against stale/None elements inside the check.
            def _ready(d, el=t):
                try:
                    return el is not None and el.is_displayed() and el.is_enabled()
                except StaleElementReferenceException:
                    return False
            wait.until(_ready)
            try:
                t.click()
            except Exception:
                driver.execute_script("arguments[0].click();", t)
            clicked = True
            break
        except Exception:
            continue
    assert clicked, f"Could not click notebook card for '{notebook_name}'"
    # For notebooks with prior chat history "Save to note" appears immediately.
    # For empty notebooks no prior messages exist, so fall back to the chat textarea.
    wait.until(lambda d: (
        d.find_elements(By.XPATH, "//span[text()='Save to note']")
        or d.find_elements(By.CSS_SELECTOR, "textarea[placeholder='Start typing...']")
        or d.find_elements(By.CSS_SELECTOR, "textarea[placeholder*='Start']")
        or d.find_elements(By.CSS_SELECTOR, "textarea[aria-label*='Ask']")
        or d.find_elements(By.CSS_SELECTOR, "textarea")
    ))


def send_query_and_get_response(driver, wait, query: str) -> str:
    """Type query into the chat textarea, submit, and return the AI response text."""
    # Snapshot completed-answer count BEFORE submitting. Each finished AI reply
    # gets its own "Save to note" button, so once this count goes up we know
    # the new answer has fully streamed.
    initial_save_count = len(driver.find_elements(*_SAVE_NOTE))

    chat_input = wait.until(lambda d: (
        d.find_elements(By.CSS_SELECTOR, "textarea[placeholder='Start typing...']")
        or d.find_elements(By.CSS_SELECTOR, "textarea[placeholder*='Start']")
        or d.find_elements(By.CSS_SELECTOR, "textarea[aria-label*='Ask']")
        or d.find_elements(By.CSS_SELECTOR, "textarea")
    )[0])
    # Scroll into view, then use ActionChains so Angular has time to wire up
    # the textarea before we start typing (plain click+send_keys can miss focus
    # when the notebook was just opened and the component hasn't fully initialised).
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", chat_input)
    try:
        (ActionChains(driver)
            .move_to_element(chat_input)
            .click()
            .pause(0.5)          # let Angular finish binding the input
            .send_keys(query)
            .send_keys(Keys.ENTER)
            .perform())
    except Exception:
        # Fallback: JS click + direct send_keys
        driver.execute_script("arguments[0].click();", chat_input)
        chat_input.send_keys(query)
        chat_input.send_keys(Keys.ENTER)

    # Wait for the AI to start responding (thinking animation appears almost
    # immediately after Enter) OR for a prior response to show Save-to-note.
    # This confirms the query was actually submitted before we wait for it to finish.
    wait.until(lambda d: (
        d.find_elements(By.XPATH, "//div[contains(@class,'thinking-animation-container')]")
        or d.find_elements(By.XPATH, "//span[text()='Save to note']")
    ))
    wait.until(EC.invisibility_of_element_located(_THINKING))

    # Strong completion signal: wait until a NEW Save-to-note button appears.
    # NotebookLM only renders this button once the answer has finished streaming,
    # so this prevents us from reading a half-streamed response.
    try:
        wait.until(lambda d: len(d.find_elements(*_SAVE_NOTE)) > initial_save_count)
    except Exception:
        # If the save-to-note signal never fires (UI change), fall through to
        # the text-stability poll below — it provides a safety net.
        pass

    # Get the LAST answer element — notebooks reused across tests accumulate chat
    # history, so the first matching element may be a previous test's response.
    answer_el = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//mat-card-content[contains(@class,'to-user-message-inner-content')]")
        or None
    ) and d.find_elements(By.XPATH,
        "//mat-card-content[contains(@class,'to-user-message-inner-content')]")[-1])

    # Belt-and-braces: poll the answer text until it stops changing for ~1.5s.
    # Catches any case where save-to-note appeared but DOM updates are still
    # propagating into the text node.
    prev_text = ""
    stable = 0
    for _ in range(60):  # up to 30s
        try:
            cur = answer_el.text.strip()
        except Exception:
            cur = ""
        if cur and cur == prev_text:
            stable += 1
            if stable >= 3:
                break
        else:
            stable = 0
            prev_text = cur
        time.sleep(0.5)

    return answer_el.text.strip()


def click_citation_and_get_passage(driver, wait) -> str:
    """Click the first citation button and return the highlighted passage text."""
    def _find_citation(d):
        for xpath in (
            "//button[@dialoglabel='Citation Details']"
            "//span[normalize-space()='1']/ancestor::button[1]",
            "//button[contains(@aria-label,'Citation') and .//span[normalize-space()='1']]",
            "//button[.//span[normalize-space()='1'] and "
            "(@dialoglabel='Citation Details' or contains(@aria-label,'Citation'))]",
            "//button[.//*[normalize-space()='1'] and contains(@class,'citation')]",
        ):
            els = [e for e in d.find_elements(By.XPATH, xpath) if e is not None]
            if els:
                return els[0]
        return False

    btn = wait.until(_find_citation)
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)

    def _find_viewer(d):
        for sel, by in (
            ("div.elements-container", By.CSS_SELECTOR),
            ("//div[contains(@class,'elements-container')]", By.XPATH),
            ("//div[contains(@class,'source') and .//span[contains(@class,'highlight')]]", By.XPATH),
            ("//div[.//span[contains(@class,'highlighted')]]", By.XPATH),
        ):
            els = [e for e in d.find_elements(by, sel) if e is not None]
            if els:
                return els[0]
        return False

    viewer = wait.until(_find_viewer)
    spans = wait.until(lambda d: (
        viewer.find_elements(By.XPATH, ".//span[contains(@class,'highlighted')]")
        or viewer.find_elements(By.XPATH, ".//*[contains(@class,'highlight')]")
        or d.find_elements(By.XPATH,
            "//div[contains(@class,'elements-container')]//span[contains(@class,'highlighted')]")
        or d.find_elements(By.XPATH, "//*[contains(@class,'highlighted')]")
    ))
    return " ".join(s.text.strip() for s in spans if s.text.strip())


def citation_count(driver) -> int:
    """Return the number of citation buttons visible in the last AI response."""
    found = (
        driver.find_elements(By.XPATH, "//button[@dialoglabel='Citation Details']")
        or driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Citation')]")
        or driver.find_elements(By.XPATH, "//button[contains(@class,'citation')]")
    )
    return len(found)


def write_and_score(
    artifacts_dir: Path,
    expected: str,
    actual: str,
    test_name: str,
    threshold: float,
) -> float:
    """Write expected/actual artifacts and compute cosine similarity score."""
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "expected.txt").write_text(expected, encoding="utf-8")
    (artifacts_dir / "actual.txt").write_text(actual, encoding="utf-8")
    from scripts.offline_scoring import compute_and_write_score
    return compute_and_write_score(artifacts_dir, threshold=threshold, test_name=test_name)


def assert_ungrounded(answer: str, keywords: list) -> None:
    """Assert the answer contains at least one phrase indicating 'no info / not in sources'."""
    lower = answer.lower()
    assert any(kw.lower() in lower for kw in keywords), (
        f"Expected an ungrounded response containing one of {keywords}, but got:\n{answer[:400]}"
    )
