# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

**Run all unit tests (fast, no browser required):**
```bash
.venv/bin/python -m pytest -q
```

**Run a single test file:**
```bash
.venv/bin/python -m pytest tests/support/test_similarity.py -q
```

**Run a single test function:**
```bash
.venv/bin/python -m pytest tests/support/test_similarity.py::test_name -q
```

**Run Selenium tests against NotebookLM (requires Chrome):**
```bash
# Weblink suite (TC1–TC20)
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -s tests/weblink/

# Google Workspace suite (TC1–TC20)
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -s tests/gworkspace/

# YouTube suite (TC1–TC20)
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -s tests/youtube/

# Upload suite (TC1–TC20)
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -s tests/upload/

# Legacy notebook suite
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -s tests/notebook/
```

Use `-s` to print AI answers and cited passages live as each test runs. Use `-q` for quieter output.

When `USER_DATA_DIR` is set, the `driver` fixture in `tests/conftest.py` reuses a persistent Selenium-only profile at `/tmp/notebooklm-selenium-session` (Chrome blocks DevTools on the real default profile). The first run requires a one-time manual Google sign-in in the launched Chrome window — the fixture waits up to 3 minutes for the URL to leave `accounts.google.com`. When `USER_DATA_DIR` is unset, a fresh temp profile is used in headless mode (sign-in flow won't work).

**Start the FastAPI server:**
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Run via Docker (API only):**
```bash
docker build -t notebooklm-api .
docker run -p 8000:8000 notebooklm-api
```

**Generate summary report from results CSV:**
```bash
NOTEBOOKLM_ARTIFACTS=./artifacts python scripts/summary_report.py --save-plot
```

**Augment test queries (uses OpenAI if `OPENAI_API_KEY` is set, otherwise fallback):**
```bash
python scripts/augment_questions.py --source artifacts/semantic_results.csv --out artifacts/augmented_questions.jsonl --n 5
```

## Architecture

The project tests [NotebookLM](https://notebooklm.google.com/) by automating queries via Selenium, capturing AI answers and source citations, then asserting semantic similarity between a known expected string and the AI answer (`actual`).

### Core library: `semantic/`

- `embeddings.py` — `EmbeddingModel` wraps `sentence-transformers` (default model: `all-MiniLM-L6-v2`). Single entrypoint for all embedding generation.
- `similarity.py` — `top_k_cosine` and `cosine_similarity_matrix` operate on numpy arrays returned by `EmbeddingModel.embed()`.
- `index.py` — Optional `FaissIndex` wrapper. Gracefully skips if `faiss` is not installed (unavailable on macOS via pip).
- `cli.py` — CLI demo; requires `--corpus <file>` (one sentence per line).

### API: `api/main.py`

FastAPI app with three endpoints (`/embed`, `/similarity`, `/similarity/search`) that all delegate to `EmbeddingModel`. The web UI is served as static files from `web/` at `/static`. The Dockerfile exposes port 8000 and runs uvicorn directly (no `--reload`).

### Test structure: `tests/`

All Selenium suites share the session-scoped `driver` / `wait` fixtures in `tests/conftest.py`.

Every test that can fail wraps its body in `try/except … pytest.xfail(...)` so the full suite always exits clean (no hard failures). Ungrounded tests (no-source, out-of-scope, hallucination) use `assert_ungrounded()` instead of similarity scoring.

Each grounded test defines a per-file `THRESHOLD` constant that overrides `SEMANTIC_SIM_THRESHOLD`. Web-sourced tests typically use 0.30 (long cited passages diverge from the short curated expected string); file-sourced tests use the default 0.65.

**Test suites:**

- `tests/support/` — Unit/integration tests for the `semantic` library, scoring helpers, and the FastAPI app. No browser required; always enabled.

- `tests/notebook/` — Legacy Selenium tests. Source corpora are Markdown/text files in `notebook_sources/`. Each test: opens notebook → sends query → clicks citation 1 → collects highlighted passage → calls `scripts/offline_scoring.compute_and_write_score()` → asserts score ≥ threshold.

- `tests/weblink/` — TC1–TC20. Covers: no source, single source, multi-source, restricted/invalid URLs, out-of-scope, hallucination, retrieval relevance, partial relevance, unsupported content. TC11–TC20 are additional runs against the same notebooks as TC1–TC10. Shared helpers in `tests/weblink/helpers.py`. `conftest.py` generates `artifacts/weblink_report.html` at session end.

- `tests/gworkspace/` — TC1–TC20. Re-exports helpers from `tests/weblink/helpers.py`. `conftest.py` generates `artifacts/gworkspace_report.html`.

- `tests/youtube/` — TC1–TC20. TC13–TC20 are additional runs against the same notebooks as TC1–TC12. Re-exports weblink helpers. `conftest.py` generates `artifacts/youtube_report.html`.

- `tests/upload/` — TC1–TC20. TC13–TC20 are additional runs against the same notebooks as TC1–TC12. Test files in `tests/upload/test_files/`. `conftest.py` generates `artifacts/upload_report.html`.

**Selenium helper functions** (`tests/weblink/helpers.py`):
- `open_notebook(driver, wait, name)` — navigates to NotebookLM home and clicks the named notebook card.
- `send_query_and_get_response(driver, wait, query)` — types query, submits, waits for the thinking animation to finish, waits for a new "Save to note" button (stream-complete signal), then polls text until stable for 1.5 s.
- `click_citation_and_get_passage(driver, wait)` — clicks citation button #1 and returns joined highlighted span text.
- `write_and_score(artifacts_dir, expected, actual, test_name, threshold)` — writes `expected.txt` / `actual.txt` and delegates to `scripts/offline_scoring`.
- `assert_ungrounded(answer, keywords)` — asserts answer contains at least one "no info / not in sources" keyword.

### Scripts: `scripts/`

- `offline_scoring.py` — Reads `expected.txt` / `actual.txt`, computes cosine similarity, writes `semantic_score.txt`, and appends to `semantic_results.csv`. Raises `AssertionError` if score is below threshold.
- `summary_report.py` — Aggregates `semantic_results.csv` into summary stats and optionally a histogram PNG.
- `augment_questions.py` — Generates paraphrased test queries via OpenAI or deterministic fallback.
- `generate_expected_actual.py` — Parses a captured NotebookLM HTML page (via BeautifulSoup) to extract `expected.txt` and `actual.txt` without a browser.

### Artifacts: `artifacts/`

| File | Written by | Purpose |
|---|---|---|
| `expected.txt` | Grounded tests | Cited source passage or curated expected string |
| `actual.txt` | Grounded tests | AI answer text |
| `semantic_score.txt` | `offline_scoring.py` | Latest single score |
| `semantic_results.csv` | `offline_scoring.py` | Append-only log of all test runs |
| `semantic_summary.json/csv` | `summary_report.py` | Aggregated metrics |
| `augmented_questions.jsonl` | `augment_questions.py` | LLM-augmented test queries |
| `weblink_report.html` | `tests/weblink/conftest.py` | Weblink HTML test report |
| `gworkspace_report.html` | `tests/gworkspace/conftest.py` | GWorkspace HTML test report |
| `youtube_report.html` | `tests/youtube/conftest.py` | YouTube HTML test report |
| `upload_report.html` | `tests/upload/conftest.py` | Upload HTML test report |

## Key environment variables

| Variable | Default | Description |
|---|---|---|
| `NOTEBOOKLM_ARTIFACTS` | `./artifacts` | Directory for all captured artifacts |
| `SEMANTIC_SIM_THRESHOLD` | `0.65` | Minimum passing cosine similarity score (per-test `THRESHOLD` overrides this) |
| `RUN_SELENIUM` | unset | Set to `1` to enable Selenium test execution |
| `USER_DATA_DIR` | unset | Chrome profile path for Selenium (must be closed first) |
| `WEBDRIVER_WAIT` | `120` | Selenium WebDriverWait timeout in seconds |

## HTML Reports

After any Selenium run, open the generated report in a browser:

```bash
open artifacts/weblink_report.html
open artifacts/gworkspace_report.html
open artifacts/youtube_report.html
open artifacts/upload_report.html
```

Each report shows: Total / Passed / Failed / Skipped summary cards, and a per-test table with TC number, description, pass/fail badge, duration, and failure reason.

## CI

The GitHub Actions workflow (`.github/workflows/ci.yml`) is fully commented out. Tests are not run automatically on push/PR.
