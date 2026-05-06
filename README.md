# NotebookLM Test Suite

Automated end-to-end tests for [NotebookLM](https://notebooklm.google.com/) using Selenium. Tests cover multiple source types, query patterns, grounding behaviour, and error states. Semantic similarity scoring is used to verify answer quality on grounded tests.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Test Suites

| Suite | Folder | TCs | Source type |
|---|---|---|---|
| Weblink | `tests/weblink/` | TC1–TC20 | Public web URLs |
| Google Workspace | `tests/gworkspace/` | TC1–TC20 | Google Docs / Sheets / Slides |
| YouTube | `tests/youtube/` | TC1–TC12 | YouTube videos |
| Upload | `tests/upload/` | TC1–TC12 | Uploaded files (PDF, TXT) |
| Notebook (legacy) | `tests/notebook/` | 7 tests | Markdown / text sources |
| Unit / API | `tests/support/` | 4 files | No browser required |

---

## Running Tests

All Selenium suites require Chrome and a signed-in Google account. On first run a Chrome window opens and waits up to 3 minutes for manual Google sign-in — the session is then reused for the rest of the run.

**Unit tests only (no browser):**
```bash
.venv/bin/python -m pytest -q
```

**Weblink suite (TC1–TC20):**
```bash
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -q tests/weblink/
```

**Google Workspace suite (TC1–TC20):**
```bash
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -q tests/gworkspace/
```

**YouTube suite (TC1–TC12):**
```bash
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -q tests/youtube/
```

**Upload suite (TC1–TC12):**
```bash
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -q tests/upload/
```

**Run a single test file:**
```bash
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -s tests/weblink/test_tc2_single_source.py
```

The `-s` flag prints the AI answer and cited passage live as each test runs.

---

## HTML Reports

Each suite generates a self-contained HTML report automatically at the end of the run:

| Suite | Report file |
|---|---|
| Weblink | `artifacts/weblink_report.html` |
| Google Workspace | `artifacts/gworkspace_report.html` |

Reports include a summary (Total / Passed / Failed / Skipped) and a per-test table showing TC number, description, pass/fail badge, and failure reason.

---

## Notebooks Required

Each test targets a pre-existing NotebookLM notebook by name. The notebooks must exist in the signed-in Google account before running the tests.

**Weblink notebooks:**

| Notebook name | Source |
|---|---|
| `WebTest - No Source` | Empty (no source) |
| `WebTest - Python Wiki` | https://en.wikipedia.org/wiki/Python_(programming_language) |
| `WebTest - Scripting Languages` | Python Wiki + JavaScript Wiki |
| `WebTest - Restricted Source` | https://www.linkedin.com/feed/ |
| `WebTest - Invalid Source` | https://www.notarealwebsite-xyzabc123456.com/fake-article |
| `WebTest - Climate Change` | https://en.wikipedia.org/wiki/Climate_change |
| `WebTest - Software Testing` | https://en.wikipedia.org/wiki/Software_testing |

**Google Workspace notebooks:**

| Notebook name | Source type |
|---|---|
| `GSuite - Employee Handbook` | Google Doc — remote work policy, benefits |
| `GSuite - Q3 Financial Report (View Only)` | Google Doc (View only) — Q3 revenue figures |
| `GSuite - PM Glossary` | Google Doc — project management glossary |
| `GSuite - Annual Report 2024` | Google Doc — FY2024 annual report |
| `GSuite - Multi Quarter Reports` | Two Google Docs — Q1 + Q2 project reports |
| `GSuite - Product Specs` | Google Doc — Product Alpha vs Beta specs |
| `GSuite - Budget Spreadsheet` | Google Doc with table — Q2 budget data |
| `GSuite - Sparse Sales Data` | Google Doc with table — incomplete sales data |
| `GSuite - Chart Only Slides` | Google Slides — image-only charts, no text values |
| `GSuite - Private Drive Doc` | Google Drive link — restricted, not shared |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `RUN_SELENIUM` | unset | Set to `1` to enable Selenium tests |
| `USER_DATA_DIR` | unset | Path to Chrome profile (close Chrome first) |
| `NOTEBOOKLM_ARTIFACTS` | `./artifacts` | Directory for test outputs and reports |
| `SEMANTIC_SIM_THRESHOLD` | `0.65` | Default cosine similarity pass threshold |
| `WEBDRIVER_WAIT` | `120` | Selenium WebDriverWait timeout in seconds |

---

## Artifacts

Runtime outputs written to `NOTEBOOKLM_ARTIFACTS` (default `./artifacts`):

| File | Written by | Purpose |
|---|---|---|
| `expected.txt` | Grounded tests | Cited source passage |
| `actual.txt` | Grounded tests | AI answer text |
| `semantic_score.txt` | `offline_scoring.py` | Latest similarity score |
| `semantic_results.csv` | `offline_scoring.py` | Append-only log of all scored runs |
| `weblink_report.html` | Weblink conftest | HTML test report |
| `gworkspace_report.html` | GWorkspace conftest | HTML test report |

---

## Summary Report

After running tests, generate aggregated stats from the CSV:

```bash
NOTEBOOKLM_ARTIFACTS=./artifacts .venv/bin/python scripts/summary_report.py
```

Add `--save-plot` to save a histogram PNG (requires `matplotlib`).

---

## FastAPI (Semantic Similarity API)

A local REST API exposing the semantic similarity engine:

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Endpoints: `POST /embed`, `POST /similarity`, `POST /similarity/search`.
Web UI available at `http://127.0.0.1:8000/static/index.html`.
