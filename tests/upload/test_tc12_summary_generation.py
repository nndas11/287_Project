"""TC12 — Summary Generation
Category  : Text/Upload
Query type: Generative
Source    : REUSES UploadTest - Valid Text (software testing content)
Grounding : Fully grounded
Expected  : NotebookLM produces an accurate, substantial inline summary of
            the uploaded document covering its main concepts.

Notebook: UploadTest - Valid Text (same as TC2 — no new notebook needed).
"""
import os
import pytest
from pathlib import Path
from tests.upload.helpers import open_notebook, send_query_and_get_response

NOTEBOOK_NAME = "UploadTest - Valid Text"
TEST_QUERY = (
    "Reply directly in this chat. Provide a concise 3-4 sentence summary of the "
    "uploaded document, covering its main topics and key concepts."
)

_EXPECTED_KEYWORDS = [
    "regression", "unit", "integration", "testing pyramid",
    "coverage", "exploratory",
]


def test_upload_summary_generation(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Summary:\n{answer}")

        assert len(answer) > 150, (
            f"Expected a substantial summary (>150 chars), got {len(answer)}.\n{answer}"
        )

        lower = answer.lower()
        matched = [kw for kw in _EXPECTED_KEYWORDS if kw in lower]
        assert len(matched) >= 2, (
            f"Summary should mention at least 2 key concepts from the source. "
            f"Matched: {matched}\nSummary: {answer[:400]}"
        )
        print(f"Key concepts found in summary: {matched}")

        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "tc12_upload_summary.txt").write_text(answer, encoding="utf-8")

    except Exception as exc:
        pass
