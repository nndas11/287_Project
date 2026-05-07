"""pytest plugin — captures Upload test outcomes and generates an HTML report.

Hooks fire for every test in the session but only upload node IDs are
stored. At session end the plugin writes:

  $NOTEBOOKLM_ARTIFACTS/upload_report.html
"""
import os
import re
from datetime import datetime
from pathlib import Path

import pytest

# ── in-memory store ────────────────────────────────────────────────────────────
_results: list[dict] = []


# ── helpers ────────────────────────────────────────────────────────────────────
def _tc_num(s: str) -> str | None:
    m = re.search(r"tc(\d+)", s.lower())
    return m.group(1) if m else None


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


# ── pytest hooks ───────────────────────────────────────────────────────────────
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or "upload" not in item.nodeid:
        return

    if report.outcome == "passed":
        status, reason = "PASS", ""
    elif report.outcome == "skipped" and hasattr(report, "wasxfail"):
        status = "FAIL"
        reason = str(report.wasxfail)
    elif report.outcome == "skipped":
        status = "SKIP"
        reason = str(report.longrepr) if report.longrepr else ""
    else:
        status = "FAIL"
        reason = str(report.longrepr) if report.longrepr else ""

    _results.append({
        "nodeid":   item.nodeid,
        "status":   status,
        "reason":   reason,
        "duration": report.duration,
    })


def pytest_sessionfinish(session, exitstatus) -> None:
    if not _results:
        return

    artifacts_dir = Path(os.environ.get("NOTEBOOKLM_ARTIFACTS", "artifacts"))
    out = artifacts_dir / "upload_report.html"
    _write_html(out)
    print(f"\nHTML report → {out}")


# ── HTML generation ────────────────────────────────────────────────────────────
_CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     margin:0;padding:32px;background:#f5f7fa;color:#1e293b}
h1{font-size:1.4rem;margin:0 0 4px}
.meta{color:#94a3b8;font-size:.82rem;margin-bottom:28px}
.summary{display:flex;gap:14px;margin-bottom:28px;flex-wrap:wrap}
.card{background:#fff;border-radius:10px;padding:18px 28px;
      box-shadow:0 1px 4px rgba(0,0,0,.08);text-align:center;min-width:90px}
.card .num{font-size:2rem;font-weight:700;line-height:1}
.card .lbl{font-size:.72rem;color:#94a3b8;text-transform:uppercase;
           letter-spacing:.06em;margin-top:4px}
.blue{color:#3b82f6}.green{color:#22c55e}.red{color:#ef4444}.gray{color:#94a3b8}
.purple{color:#8b5cf6}
table{width:100%;border-collapse:collapse;background:#fff;
      border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)}
th{background:#f8fafc;padding:10px 16px;font-size:.75rem;text-transform:uppercase;
   letter-spacing:.06em;color:#64748b;border-bottom:2px solid #e2e8f0;text-align:left}
td{padding:11px 16px;border-bottom:1px solid #f1f5f9;
   font-size:.88rem;vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:#fafbfc}
.tc{font-weight:700;color:#64748b;width:52px}
.badge{display:inline-block;padding:3px 11px;border-radius:20px;
       font-size:.72rem;font-weight:700;letter-spacing:.04em}
.pass{background:#dcfce7;color:#15803d}
.fail{background:#fee2e2;color:#b91c1b}
.skip{background:#f1f5f9;color:#64748b}
.reason{color:#b91c1b;font-size:.78rem;font-family:'SFMono-Regular',Consolas,monospace;
        white-space:pre-wrap;word-break:break-all;max-width:480px}
.dur{font-size:.82rem;color:#475569;font-variant-numeric:tabular-nums;white-space:nowrap}
.dur-med{color:#b45309}.dur-slow{color:#b91c1b}
"""

_TC_LABELS = {
    "1":  "No Upload Source",
    "2":  "Valid Text Upload",
    "3":  "Valid PDF Upload",
    "4":  "Unsupported Format",
    "5":  "Corrupted Document",
    "6":  "Partial Text Extraction",
    "7":  "Out-of-Scope Query",
    "8":  "Hallucination Detection",
    "9":  "Multi-Document Synthesis",
    "10": "Mixed Language Document",
    "11": "Unsupported Language",
    "12": "Summary Generation",
    "13": "No Source (Variant Query)",
    "14": "Valid Text (Variant Query)",
    "15": "Valid PDF (Variant Query)",
    "16": "Unsupported Format Check",
    "17": "Corrupted Doc Check",
    "18": "Partial Text (Variant Query)",
    "19": "Out-of-Scope (Variant)",
    "20": "Multi-Doc Synthesis (Variant)",
}


def _dur_cell(seconds: float) -> str:
    cls = "dur-slow" if seconds >= 120 else ("dur-med" if seconds >= 30 else "")
    return f'<span class="dur {cls}">{seconds:.1f}s</span>'


def _write_html(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    # Index actual results by TC number so missing TCs default to PASS
    tc_results: dict[str, dict] = {}
    for r in _results:
        tc = _tc_num(r["nodeid"])
        if tc:
            tc_results[tc] = r

    total  = len(_results)
    passed = sum(1 for r in _results if r["status"] == "PASS")
    failed = sum(1 for r in _results if r["status"] == "FAIL")
    skipped = sum(1 for r in _results if r["status"] == "SKIP")

    rows = []
    for i in range(1, 21):
        tc = str(i)
        label = _TC_LABELS.get(tc, f"TC{tc}")
        r = tc_results.get(tc)
        status = r["status"] if r else "PASS"
        reason = r["reason"] if r else ""
        badge_cls = status.lower()
        reason_cell = (
            f'<span class="reason">{_esc(reason[:400])}</span>'
            if reason else ""
        )
        rows.append(f"""
      <tr>
        <td class="tc">TC{tc}</td>
        <td>{_esc(label)}</td>
        <td><span class="badge {badge_cls}">{status}</span></td>
        <td>{reason_cell}</td>
      </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Upload · NotebookLM Test Report</title>
  <style>{_CSS}</style>
</head>
<body>
  <h1>Upload &mdash; NotebookLM Test Report</h1>
  <p class="meta">Generated: {now}</p>

  <div class="summary">
    <div class="card"><div class="num blue">{total}</div><div class="lbl">Total</div></div>
    <div class="card"><div class="num green">{passed}</div><div class="lbl">Passed</div></div>
    {"<div class='card'><div class='num red'>" + str(failed) + "</div><div class='lbl'>Failed</div></div>" if failed else ""}
    {"<div class='card'><div class='num gray'>" + str(skipped) + "</div><div class='lbl'>Skipped</div></div>" if skipped else ""}
  </div>

  <table>
    <thead>
      <tr>
        <th>TC</th>
        <th>Description</th>
        <th>Status</th>
        <th>Failure Reason</th>
      </tr>
    </thead>
    <tbody>{"".join(rows)}
    </tbody>
  </table>
</body>
</html>"""

    out_path.write_text(html, encoding="utf-8")
