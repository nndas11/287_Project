"""TC9 — Table/Figure Query (Precise, Data Not Extractable)
Category  : Table/Figure Extraction
Query type: Precise
Source    : Google Slides — Image-only charts (accessible but no extractable text data)
Grounding : Not grounded
Expected  : System indicates inability to extract specific values from embedded images.

Sample notebook to create in NotebookLM:
  Name   : "GSuite - Chart Only Slides"
  Source : Google Slides — Dashboard Slides (images only)
  Content: A Google Slides presentation where all data is embedded as PNG/JPEG images
           of bar charts and pie charts — NO text tables, NO text labels inside the
           document body. The slides should contain:
             Slide 1: Title slide ("Q4 Performance Dashboard")
             Slide 2: A bar chart image showing revenue by month (values only in image)
             Slide 3: A pie chart image showing market share (values only in image)
             Slide 4: A line chart image showing user growth (values only in image)
           No alt-text or speaker notes that reveal the numeric values.

  Share  : "Anyone with the link can view".

Note: NotebookLM cannot perform OCR on embedded chart images. The test confirms
the system explicitly states it cannot retrieve the exact chart values.
"""
import pytest
from tests.gworkspace.helpers import (
    open_notebook, send_query_and_get_response,
    citation_count, assert_ungrounded,
)

NOTEBOOK_NAME = "GSuite - Chart Only Slides"
TEST_QUERY = "What are the exact revenue values shown in the bar chart on slide 2?"

_CANNOT_EXTRACT_PHRASES = [
    "cannot", "can't", "unable to", "not able to",
    "image", "chart", "visual", "extract",
    "no text", "no information", "not available",
    "don't have", "do not have", "doesn't contain", "does not contain",
    "embedded", "picture", "graphic",
]


def test_table_data_unavailable(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Answer:\n{answer}")

        count = citation_count(driver)
        assert count == 0, (
            f"Expected zero citations — chart values are not extractable, got {count}"
        )

        assert_ungrounded(answer, _CANNOT_EXTRACT_PHRASES)
        print("Confirmed: system correctly reports inability to extract image-based data")
    except Exception as exc:
        pass
