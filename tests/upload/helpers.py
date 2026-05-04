"""Shared Selenium helpers for Text/Upload-source NotebookLM tests.

NotebookLM's chat UI is identical regardless of source type, so we re-export
the helpers from `tests.weblink.helpers`. Upload-specific helpers (file-input
interaction, text-paste modal) live here if needed in future.
"""
from tests.weblink.helpers import (  # noqa: F401
    open_notebook,
    send_query_and_get_response,
    click_citation_and_get_passage,
    citation_count,
    write_and_score,
    assert_ungrounded,
)
