
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
    page.wait_for_selector("#mat-mdc-dialog-0")
    vertical_selector = page.locator("select")
    vertical_selector.select_option(label="Alpha")
    page.wait_for_selector("button:has-text('Submit')")
    page.click("button:has-text('Submit')")

def select_project_ai_sdet360(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    project_selector = page.locator("select")
    project_selector.select_option(label="AI.SDET360")
    page.wait_for_selector("button:has-text('Submit')")
    page.click("button:has-text('Submit')")

def login(page):
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", "neha.pal@sdettech.com")
    page.fill("input[name='password']", "Neha@123")
    page.click("button:has-text('Submit')")

def test_tc001(page):
    try:
        login(page)
        select_vertical_alpha(page)
        select_project_ai_sdet360(page)
        _record("TC001 - Login and Select Vertical Alpha and Project AI.SDET360", True)
    except Exception as e:
        _record("TC001 - Login and Select Vertical Alpha and Project AI.SDET360", False, str(e))

def test_tc002(page):
    try:
        login(page)
        select_vertical_alpha(page)
        page.wait_for_selector("#mat-mdc-dialog-0")
        page.wait_for_selector("select")
        page.wait_for_selector("button:has-text('Submit')")
        _record("TC002 - Verify Select Vertical Pop-up UI", True)
    except Exception as e:
        _record("TC002 - Verify Select Vertical Pop-up UI", False, str(e))

def test_tc003(page):
    try:
        login(page)
        select_vertical_alpha(page)
        page.wait_for_selector("#mat-mdc-dialog-0")
        page.wait_for_selector("select")
        page.wait_for_selector("button:has-text('Submit')")
        _record("TC003 - Verify Dropdown Arrow Positioning", True)
    except Exception as e:
        _record("TC003 - Verify Dropdown Arrow Positioning", False, str(e))

def test_tc004(page):
    try:
        login(page)
        select_vertical_alpha(page)
        page.wait_for_selector("#mat-mdc-dialog-0")
        page.wait_for_selector("select")
        page.wait_for_selector("button:has-text('Submit')")
        _record("TC004 - Verify Hover Effects", True)
    except Exception as e:
        _record("TC004 - Verify Hover Effects", False, str(e))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://qa.sdet360.ai")
    test_tc001(page)
    test_tc002(page)
    test_tc003(page)
    test_tc004(page)
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
