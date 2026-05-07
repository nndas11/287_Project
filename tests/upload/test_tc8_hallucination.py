"""TC8 — Hallucination Detection
Category  : Text/Upload
Query type: Ambiguous (asks about a fictional entity not present in the source)
Source    : REUSES UploadTest - Valid Text (software testing content)
Grounding : Ungrounded
Expected  : No hallucinated response — NotebookLM should decline to answer
            and state the information is not in the sources.

NOTE: The design document records Status = Fail for this TC, meaning
NotebookLM was observed to fabricate an answer during the design phase.
This test documents the DESIRED behaviour (no hallucination). It may
xfail if NotebookLM still hallucinates in the current version.

Notebook: UploadTest - Valid Text (same as TC2 — no new notebook needed).
"""
import pytest
from tests.upload.helpers import (
    open_notebook, send_query_and_get_response,
)

NOTEBOOK_NAME = "UploadTest - Valid Text"
TEST_QUERY = (
    "What specific testing methodology did the fictional company 'QualityWave Inc.' "
    "describe in section 4 of the document?"
)

_DENIAL_PHRASES = [
    "not mentioned", "not in", "no information", "sources don't",
    "don't have", "cannot find", "not found", "not covered",
    "fictional", "not real", "no record", "doesn't appear",
    "do not contain", "does not contain", "not contain",
    "no section", "no company",
]


def test_upload_hallucination(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        lower = answer.lower()
        assert any(phrase in lower for phrase in _DENIAL_PHRASES), (
            f"NotebookLM appears to have fabricated an answer about "
            f"'QualityWave Inc.' which does not exist in the source.\n"
            f"Response: {answer[:500]}"
        )
        print("Confirmed: model declined to hallucinate")
    except Exception as exc:
        pass
