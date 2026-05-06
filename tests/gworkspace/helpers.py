"""Shared Selenium helpers for Google Workspace-source NotebookLM tests.

NotebookLM's chat UI is identical regardless of source type, so we re-export
the helpers from `tests.weblink.helpers`. If Google Workspace-specific helpers
are needed later (e.g. Drive-permission waits), add them here.
"""
from tests.weblink.helpers import (  # noqa: F401
    open_notebook,
    send_query_and_get_response,
    click_citation_and_get_passage,
    citation_count,
    write_and_score,
    assert_ungrounded,
)
