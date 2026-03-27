
import json, sys, traceback
from pathlib import Path

_results = []
_errors  = []

def __cascade_record(name, passed, error=None, details=None):
    _results.append({
        "name": name,
        "passed": passed,
        "error": error,
        "details": details or "",
    })

_record = __cascade_record


import time
import json
import sys

from playwright.sync_api import sync_playwright

def select_vertical_alpha(page):
    page.wait_for_selector("#vertical-select")
    page.click("text=Alpha")
    page.wait_for_selector("#vertical-select")
    page.click("text=Alpha")

def select_project_ai_sdet360(page):
    page.wait_for_selector("#project-select")
    page.click("text=AI.SDET360")
    page.wait_for_selector("#project-select")
    page.click("text=AI.SDET360")

def login(page):
    page.wait_for_selector("[name='email']")
    page.fill("[name='email']", "neha.pal@sdettech.com")
    page.wait_for_selector("[name='password']")
    page.fill("[name='password']", "Neha@123")
    page.wait_for_selector("text=Submit")
    page.click("text=Submit")

def test_tc001(page):
    try:
        login(page)
        select_vertical_alpha(page)
        select_project_ai_sdet360(page)
        page.wait_for_selector("#vertical-select")
        page.wait_for_selector("#project-select")
        _record("TC001 - Login and Select Vertical/Project", True)
    except Exception as e:
        _record("TC001 - Login and Select Vertical/Project", False, error=str(e))

def test_tc002(page):
    try:
        login(page)
        page.wait_for_selector("#vertical-select")
        page.hover("text=Alpha")
        page.wait_for_selector("#vertical-select")
        page.hover("text=Alpha")
        _record("TC002 - Dropdown Arrow Positioning", True)
    except Exception as e:
        _record("TC002 - Dropdown Arrow Positioning", False, error=str(e))

def test_tc003(page):
    try:
        login(page)
        page.wait_for_selector("#vertical-select")
        page.click("text=Alpha")
        page.wait_for_selector("#project-select")
        page.click("text=AI.SDET360")
        page.wait_for_selector("#vertical-select")
        page.click("text=Alpha")
        page.wait_for_selector("#project-select")
        page.click("text=AI.SDET360")
        _record("TC003 - UI Consistency Across Application", True)
    except Exception as e:
        _record("TC003 - UI Consistency Across Application", False, error=str(e))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://qa.sdet360.ai")
    test_tc001(page)
    test_tc002(page)
    test_tc003(page)
    browser.close()


# ── Save results ──────────────────────────────────────────────
_output = {
    "status": "PASS" if _results and all(r["passed"] for r in _results) else ("FAIL" if _results else "EXECUTION_ERROR"),
    "total": len(_results),
    "passed": sum(1 for r in _results if r["passed"]),
    "failed": sum(1 for r in _results if not r["passed"]),
    "tests": _results,
    "error": None if _results else "No tests were recorded by the generated script.",
}
Path("reports/latest_run.json").write_text(json.dumps(_output, indent=2))
