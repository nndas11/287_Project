#!/usr/bin/env python3
"""
Creates all required NotebookLM notebooks for YouTube and Upload test suites.

Run ONCE after signing into the new Chrome profile:
    python scripts/setup_notebooks.py
"""
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SESSION_PROFILE = "/tmp/notebooklm-selenium-session-2"
NOTEBOOKLM_URL  = "https://notebooklm.google.com/"
TEST_FILES      = Path(__file__).parent.parent / "tests" / "upload" / "test_files"

# ── What to create ─────────────────────────────────────────────────────────────

YOUTUBE_NOTEBOOKS = [
    ("YTTest - Manual Captions",      "https://www.youtube.com/watch?v=p7HKvqRI_Bo"),
    ("YTTest - Auto Captions",        "https://www.youtube.com/watch?v=x7X9w_GIm1s"),
    ("YTTest - Low Quality Captions", "https://www.youtube.com/watch?v=Mde2q7GFlQ4"),
    # Replace REPLACE_ME with any Hinglish/mixed-language YouTube video URL
    ("YTTest - Mixed Language",       "https://www.youtube.com/watch?v=REPLACE_ME"),
    ("YTTest - Invalid URL",          None),  # empty notebook
]

# source_type: "website" → Websites dialog (YouTube URLs go here)
#              "text"    → Copied text dialog
#              "file"    → Upload files dialog
UPLOAD_NOTEBOOKS = [
    ("UploadTest - No Source",            []),
    ("UploadTest - Valid Text",           [("text", "software_testing.txt")]),
    ("UploadTest - Valid PDF",            [("file", "software_testing.pdf")]),
    ("UploadTest - Unsupported Format",   []),
    ("UploadTest - Corrupted Doc",        []),
    ("UploadTest - Partial Text",         [("text", "partial_coverage.txt")]),
    ("UploadTest - Multi Doc",            [("text", "software_testing.txt"),
                                           ("text", "agile_methodology.txt")]),
    ("UploadTest - Mixed Language",       [("text", "mixed_language.txt")]),
    ("UploadTest - Unsupported Language", [("text", "klingon_text.txt")]),
]


# ── Driver ─────────────────────────────────────────────────────────────────────

def make_driver():
    opts = Options()
    opts.add_argument(f"--user-data-dir={SESSION_PROFILE}")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    d = webdriver.Chrome(service=Service(), options=opts)
    d.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return d


# ── Navigation helpers ─────────────────────────────────────────────────────────

def go_home(driver, wait):
    driver.get(NOTEBOOKLM_URL)
    wait.until(lambda d: "notebooklm.google.com" in d.current_url
                         and "accounts.google.com" not in d.current_url)
    time.sleep(2)


def notebook_exists(driver, name):
    return bool(driver.find_elements(By.XPATH,
        f"//span[contains(@class,'project-button-title') and "
        f"contains(normalize-space(.), '{name}')]"
    ))


def click_new_notebook(driver, wait):
    btn = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//button[contains(normalize-space(),'Create new')]"
            "|//button[contains(normalize-space(),'New notebook')]"
            "|//button[contains(@aria-label,'Create new')]"
            "|//button[contains(@aria-label,'New notebook')]"
        )
    ))
    try:
        btn[0].click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn[0])
    time.sleep(2)


def wait_for_notebook_page(driver, wait):
    """Wait until the notebook page chat area is visible."""
    wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "textarea"))
    time.sleep(1)


# ── Source dialog helpers ──────────────────────────────────────────────────────

def _source_dialog_visible(driver):
    """Return True if the add-source dialog is already open."""
    return bool(driver.find_elements(By.XPATH,
        "//button[contains(normalize-space(),'Copied text')]"
        "|//button[contains(normalize-space(),'Upload files')]"
        "|//button[contains(normalize-space(),'Websites')]"
    ))


def _open_source_dialog(driver, wait):
    """Open the add-source dialog if not already open."""
    if _source_dialog_visible(driver):
        return
    btn = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//button[contains(normalize-space(),'Add source')]"
            "|//button[contains(@aria-label,'Add source')]"
            "|//*[contains(@class,'add-source') and (self::button or @role='button')]"
        )
    ))
    try:
        btn[0].click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn[0])
    time.sleep(1.5)


def dismiss_source_dialog(driver):
    """Close the source dialog without adding anything."""
    # Try common close/dismiss buttons
    for xpath in (
        "//button[@aria-label='Close']",
        "//button[contains(@aria-label,'close') or contains(@aria-label,'Close')]",
        "//mat-icon[normalize-space()='close']/ancestor::button[1]",
        "//button[contains(normalize-space(),'Done')]",
        "//button[contains(normalize-space(),'Cancel')]",
    ):
        els = driver.find_elements(By.XPATH, xpath)
        if els:
            try:
                els[0].click()
                time.sleep(1)
                return
            except Exception:
                pass
    # Fallback: Escape key
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(1)


def _click_insert(driver, wait):
    """Click the Insert/Add confirm button in a source dialog."""
    btn = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//button[normalize-space()='Insert']"
            "|//button[normalize-space()='Add']"
            "|//button[normalize-space()='Confirm']"
        )
    ))
    try:
        btn[0].click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn[0])
    time.sleep(3)


# ── Add source functions ───────────────────────────────────────────────────────

def add_website_source(driver, wait, url):
    """Add a URL (including YouTube) via the Websites dialog."""
    _open_source_dialog(driver, wait)

    websites_btn = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//button[contains(normalize-space(),'Websites')]"
            "|//*[@role='button' and contains(normalize-space(),'Websites')]"
            "|//button[contains(normalize-space(),'Website')]"
        )
    ))
    try:
        websites_btn[0].click()
    except Exception:
        driver.execute_script("arguments[0].click();", websites_btn[0])
    time.sleep(1)

    url_input = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//textarea[contains(@placeholder,'links') or contains(@placeholder,'Links') "
            "or contains(@placeholder,'URL') or contains(@placeholder,'url') "
            "or contains(@placeholder,'Paste')]"
        )
        or d.find_elements(By.XPATH,
            "//input[@type='url']"
            "|//input[contains(@placeholder,'URL') or contains(@placeholder,'url')]"
        )
    ))
    url_input[0].clear()
    url_input[0].send_keys(url)
    time.sleep(0.5)
    _click_insert(driver, wait)
    print(f"    Website source added: {url[:70]}")


def add_text_source(driver, wait, file_path):
    """Add file contents via the Copied text dialog."""
    text = Path(file_path).read_text(encoding="utf-8")
    _open_source_dialog(driver, wait)

    txt_btn = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//button[contains(normalize-space(),'Copied text')]"
            "|//*[@role='button' and contains(normalize-space(),'Copied text')]"
        )
    ))
    try:
        txt_btn[0].click()
    except Exception:
        driver.execute_script("arguments[0].click();", txt_btn[0])
    time.sleep(1)

    # Find the text entry area — could be textarea or contenteditable
    ta = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//textarea[contains(@placeholder,'Paste') or contains(@placeholder,'paste') "
            "or contains(@placeholder,'text') or contains(@placeholder,'Text') "
            "or contains(@placeholder,'content')]"
        )
        or d.find_elements(By.CSS_SELECTOR,
            "textarea:not([placeholder='Start typing...'])"
        )
    ))
    # Use JS to set value (faster than character-by-character send_keys)
    driver.execute_script("arguments[0].value = arguments[1];", ta[0], text)
    ta[0].send_keys(" ")
    ta[0].send_keys(Keys.BACKSPACE)
    time.sleep(0.5)
    _click_insert(driver, wait)
    print(f"    Text source added: {Path(file_path).name}")


def add_file_source(driver, wait, file_path):
    """Upload a file via the Upload files dialog."""
    abs_path = str(Path(file_path).resolve())
    _open_source_dialog(driver, wait)

    upload_btn = wait.until(lambda d: (
        d.find_elements(By.XPATH,
            "//button[contains(normalize-space(),'Upload files')]"
            "|//button[contains(normalize-space(),'Upload')]"
            "|//*[@role='button' and contains(normalize-space(),'Upload')]"
        )
    ))
    try:
        upload_btn[0].click()
    except Exception:
        driver.execute_script("arguments[0].click();", upload_btn[0])
    time.sleep(1)

    file_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "input[type='file']")
    ))
    file_input.send_keys(abs_path)
    time.sleep(5)
    _click_insert(driver, wait)
    print(f"    File uploaded: {Path(file_path).name}")


# ── Title rename ───────────────────────────────────────────────────────────────

def set_title(driver, wait, name):
    """Rename the notebook to 'name'."""
    time.sleep(2)
    # Try clicking the title text (Untitled notebook / auto-generated title)
    for xpath in (
        "//textarea[@aria-label='Notebook title']",
        "//input[@aria-label='Notebook title']",
        "//*[contains(@class,'notebook-title')]//textarea",
        "//*[contains(@class,'notebook-title')]//input",
        # Fallback: click on whatever text is showing as the title
        "//h1[contains(@class,'title')]",
        "//*[contains(@class,'title') and "
        " (contains(normalize-space(),'Untitled') or contains(@class,'notebook'))]",
    ):
        els = driver.find_elements(By.XPATH, xpath)
        if not els:
            continue
        el = els[0]
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            time.sleep(0.5)
            # After clicking a non-input element, an input may appear
            if el.tag_name not in ("input", "textarea"):
                for inp_xpath in (
                    "//textarea[@aria-label='Notebook title']",
                    "//input[@aria-label='Notebook title']",
                ):
                    inps = driver.find_elements(By.XPATH, inp_xpath)
                    if inps:
                        el = inps[0]
                        break
            el.send_keys(Keys.CONTROL + "a")
            el.send_keys(Keys.COMMAND + "a")
            el.clear()
            el.send_keys(name)
            el.send_keys(Keys.ENTER)
            time.sleep(1)
            print(f"    Title set: {name}")
            return
        except Exception:
            continue
    print(f"    ⚠ Could not set title automatically — rename to '{name}' manually")


# ── Notebook creators ──────────────────────────────────────────────────────────

def create_youtube_notebook(driver, wait, name, url):
    go_home(driver, wait)
    if notebook_exists(driver, name):
        print(f"  ✓ Already exists — skipping: {name}")
        return

    print(f"  Creating: {name}")
    click_new_notebook(driver, wait)
    wait_for_notebook_page(driver, wait)

    if url and "REPLACE_ME" not in url:
        try:
            add_website_source(driver, wait, url)
        except Exception as e:
            print(f"    ⚠ Could not add source: {e}")
    else:
        try:
            dismiss_source_dialog(driver)
        except Exception:
            pass
        if url and "REPLACE_ME" in url:
            print(f"    ⚠ No source added — replace REPLACE_ME with a real URL and re-run")

    set_title(driver, wait, name)
    print(f"  ✓ Done: {name}")


def create_upload_notebook(driver, wait, name, sources):
    go_home(driver, wait)
    if notebook_exists(driver, name):
        print(f"  ✓ Already exists — skipping: {name}")
        return

    print(f"  Creating: {name}")
    click_new_notebook(driver, wait)
    wait_for_notebook_page(driver, wait)

    if not sources:
        try:
            dismiss_source_dialog(driver)
        except Exception:
            pass
    else:
        for source_type, file_name in sources:
            try:
                fp = TEST_FILES / file_name
                if source_type == "text":
                    add_text_source(driver, wait, fp)
                elif source_type == "file":
                    add_file_source(driver, wait, fp)
                elif source_type == "website":
                    add_website_source(driver, wait, file_name)
            except Exception as e:
                print(f"    ⚠ Could not add {file_name}: {e}")

    set_title(driver, wait, name)
    print(f"  ✓ Done: {name}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    driver = make_driver()
    wait   = WebDriverWait(driver, 60)

    driver.get(NOTEBOOKLM_URL)
    if "accounts.google.com" in (driver.current_url or ""):
        print("=" * 60)
        print("Sign in to Google in the Chrome window.")
        print("Waiting up to 5 minutes...")
        print("=" * 60)
        WebDriverWait(driver, 300).until(
            lambda d: "notebooklm.google.com" in d.current_url
                      and "accounts.google.com" not in d.current_url
        )
        print("Signed in — starting...\n")

    try:
        print("\n── YouTube Notebooks ─────────────────────────────────────")
        for name, url in YOUTUBE_NOTEBOOKS:
            try:
                create_youtube_notebook(driver, wait, name, url)
            except Exception as e:
                print(f"  ✗ Failed: {name} — {e}")

        print("\n── Upload Notebooks ──────────────────────────────────────")
        for name, sources in UPLOAD_NOTEBOOKS:
            try:
                create_upload_notebook(driver, wait, name, sources)
            except Exception as e:
                print(f"  ✗ Failed: {name} — {e}")

        print("\n✓ Setup complete.")
        print("  Manually add source to 'YTTest - Mixed Language' if REPLACE_ME was not updated.")
    finally:
        time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    main()
