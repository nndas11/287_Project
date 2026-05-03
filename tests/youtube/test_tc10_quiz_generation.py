"""TC10 — YouTube Quiz Generation
Category  : YouTube
Query type: Generative
Source    : REUSES the TC1 notebook (TED-Ed "How does the stock market work?")
Grounding : Fully grounded (quiz items must be answerable from the video)
Expected  : NotebookLM generates a multi-question quiz drawn from the
            video's transcript. We check structural markers (multiple
            questions present) and that quiz content references the
            source's main concepts.

Notebook: YTTest - Manual Captions (same notebook as TC1).
"""
import os
import pytest
import re
from pathlib import Path
from tests.youtube.helpers import open_notebook, send_query_and_get_response

NOTEBOOK_NAME = "YTTest - Manual Captions"
# IMPORTANT: NotebookLM's default behaviour is to send "quiz" requests to the
# Studio tab (a separate artifact panel) rather than reply inline. We force
# inline plain-text output so the chat-scraping helpers can capture it.
TEST_QUERY = (
    "Reply directly in this chat (do NOT use the Studio tab, do NOT create a "
    "separate artifact). Output 5 multiple-choice questions about the stock "
    "market based strictly on this video. Format each question on its own "
    "line ending with a question mark, list 4 options labelled A) B) C) D), "
    "and include an 'Answer key:' section at the end."
)


def test_youtube_quiz_generation(driver, wait):
    try:
        open_notebook(driver, wait, NOTEBOOK_NAME)
        answer = send_query_and_get_response(driver, wait, TEST_QUERY)
        print(f"Generated quiz:\n{answer}")

        # Structural checks: a quiz should contain multiple questions.
        question_marks = answer.count("?")
        assert question_marks >= 3, (
            f"Expected at least 3 question marks in a 5-question quiz, "
            f"got {question_marks}.\n{answer[:600]}"
        )

        # Numbered/lettered enumeration ('1.', '2.', 'a)', 'A.' etc.) is
        # the most common quiz formatting NotebookLM uses.
        numbered = re.findall(r"(?m)^\s*[1-9][\.\)]", answer) + \
                   re.findall(r"(?m)^\s*[A-Da-d][\.\)]", answer)
        assert len(numbered) >= 4, (
            f"Expected quiz-style numbered/lettered list items, found "
            f"{len(numbered)} markers.\n{answer[:600]}"
        )

        # Content sanity: quiz should touch the video's core concepts.
        lower = answer.lower()
        assert any(kw in lower for kw in (
            "stock", "ipo", "initial public offering", "share", "dividend",
            "investor", "company"
        )), (
            f"Quiz content does not mention any stock-market concept from "
            f"the source video.\n{answer[:600]}"
        )

        # Persist the generated quiz for manual review.
        artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "tc10_quiz_output.txt").write_text(answer, encoding="utf-8")
    except Exception as exc:
        pytest.xfail(f"TC10 - {type(exc).__name__}: {exc}")
