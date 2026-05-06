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
  .venv/bin/python -m pytest -q tests/weblink/

# Google Workspace suite (TC1–TC20)
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -q tests/gworkspace/

# YouTube suite (TC1–TC12)
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -q tests/youtube/

# Upload suite (TC1–TC12)
RUN_SELENIUM=1 USER_DATA_DIR=/path/to/chrome-profile NOTEBOOKLM_ARTIFACTS=./artifacts \
  .venv/bin/python -m pytest -q tests/upload/
```

When `USER_DATA_DIR` is set, the `driver` fixture in `tests/conftest.py` reuses a persistent Selenium-only profile at `/tmp/notebooklm-selenium-session` (Chrome blocks DevTools on the real default profile). The first run requires a one-time manual Google sign-in in the launched Chrome window — the fixture waits up to 3 minutes for the URL to leave `accounts.google.com`. When `USER_DATA_DIR` is unset, a fresh temp profile is used in headless mode (sign-in flow won't work).

**Start the FastAPI server:**
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
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

- `embeddings.py` — `EmbeddingModel` wraps `sentence-transformers` (default model: `all-MiniLM-L6-v2`). This is the single entrypoint for all embedding generation.
- `similarity.py` — `top_k_cosine` and `cosine_similarity_matrix` operate on numpy arrays returned by `EmbeddingModel.embed()`.
- `index.py` — Optional `FaissIndex` wrapper. Gracefully skips if `faiss` is not installed (unavailable on macOS via pip).
- `cli.py` — CLI demo; requires `--corpus <file>` (one sentence per line).

### API: `api/main.py`

FastAPI app with three endpoints (`/embed`, `/similarity`, `/similarity/search`) that all delegate to `EmbeddingModel`. The web UI is served as static files from `web/` at `/static`.

### Test structure: `tests/`

All Selenium suites share the `driver` / `wait` session-scoped fixtures in `tests/conftest.py`.

- `tests/support/` — Unit/integration tests for the `semantic` library, scoring helpers, and the FastAPI app. No browser required; always enabled.

- `tests/notebook/` — Selenium tests gated behind `RUN_SELENIUM=1`. Each test: opens a notebook → sends a query → clicks citation 1 → collects highlighted passage text → calls `scripts/offline_scoring.compute_and_write_score()` → asserts score ≥ threshold. Source corpora in `notebook_sources/`.

- `tests/weblink/` — TC1–TC20 (gated behind `RUN_SELENIUM=1`). Covers: no source, single source, multi-source, restricted/invalid URLs, out-of-scope, hallucination, retrieval relevance, partial relevance, unsupported content. TC1–TC10 are the primary cases; TC11–TC20 are additional runs against the same notebooks.
  - Shared helpers in `tests/weblink/helpers.py`: `open_notebook`, `send_query_and_get_response`, `click_citation_and_get_passage`, `citation_count`, `write_and_score`, `assert_ungrounded`.
  - `tests/weblink/conftest.py` generates `artifacts/weblink_report.html` at session end.
  - Notebooks required: `WebTest - No Source`, `WebTest - Python Wiki`, `WebTest - Scripting Languages`, `WebTest - Restricted Source`, `WebTest - Invalid Source`, `WebTest - Climate Change`, `WebTest - Software Testing`.

- `tests/gworkspace/` — TC1–TC20 (gated behind `RUN_SELENIUM=1`). Covers: exact retrieval, view-only access, unclear queries, summarization, multi-source summary, comparison, table extraction (full/partial/unavailable), and restricted Drive documents. TC1–TC10 are the primary cases; TC11–TC20 are additional runs.
  - Re-exports helpers from `tests/weblink/helpers.py` (chat UI is identical regardless of source type).
  - `tests/gworkspace/conftest.py` generates `artifacts/gworkspace_report.html` at session end.
  - Notebooks required: `GSuite - Employee Handbook`, `GSuite - Q3 Financial Report (View Only)`, `GSuite - PM Glossary`, `GSuite - Annual Report 2024`, `GSuite - Multi Quarter Reports`, `GSuite - Product Specs`, `GSuite - Budget Spreadsheet`, `GSuite - Sparse Sales Data`, `GSuite - Chart Only Slides`, `GSuite - Private Drive Doc`.

- `tests/youtube/` — TC1–TC12 (gated behind `RUN_SELENIUM=1`). Covers: manual captions, auto captions, low-quality captions, no captions, invalid URL, restricted video, mixed/unsupported language, comparison queries, quiz generation, out-of-scope, complex explanation. Re-exports weblink helpers.

- `tests/upload/` — TC1–TC12 (gated behind `RUN_SELENIUM=1`). Covers: no source, valid text/PDF upload, unsupported format, corrupted doc, partial text, out-of-scope, hallucination, multi-document, mixed/unsupported language, summary generation. Test files in `tests/upload/test_files/`.

### Scripts: `scripts/`

- `offline_scoring.py` — Importable helper. Reads `expected.txt` / `actual.txt`, computes cosine similarity, writes `semantic_score.txt`, and appends a row to `semantic_results.csv`. Raises `AssertionError` if score is below threshold.
- `summary_report.py` — Aggregates `semantic_results.csv` into summary stats and optionally a histogram PNG.
- `augment_questions.py` — Generates paraphrased test queries. Uses OpenAI if `OPENAI_API_KEY` is set; otherwise uses a deterministic fallback.
- `generate_expected_actual.py` — Parses a captured NotebookLM HTML page (via BeautifulSoup) to extract `expected.txt` and `actual.txt` without running a browser.

### Artifacts: `artifacts/`

Runtime outputs written by tests and scripts:

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

## Key environment variables

| Variable | Default | Description |
|---|---|---|
| `NOTEBOOKLM_ARTIFACTS` | `./artifacts` | Directory for all captured artifacts |
| `SEMANTIC_SIM_THRESHOLD` | `0.65` | Minimum passing cosine similarity score |
| `RUN_SELENIUM` | unset | Set to `1` to enable Selenium test execution |
| `USER_DATA_DIR` | unset | Chrome profile path for Selenium (must be closed first) |
| `WEBDRIVER_WAIT` | `120` | Selenium WebDriverWait timeout in seconds |

## HTML Reports

After any Selenium run, open the generated report in a browser:

```bash
open artifacts/weblink_report.html
open artifacts/gworkspace_report.html
```

Each report shows: Total / Passed / Failed / Skipped summary cards, and a per-test table with TC number, description, pass/fail badge, and failure reason for any failing test.

## CI

The GitHub Actions workflow (`.github/workflows/ci.yml`) is fully commented out. Tests are not run automatically on push/PR.
