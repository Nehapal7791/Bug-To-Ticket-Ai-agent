
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
from playwright.sync_api import sync_playwright

def select_vertical_alpha(page):
    # Select vertical 'Alpha'
    vertical_selector = page.query_selector('text="Select Vertical"')
    vertical_selector.click()
    time.sleep(0.5)
    alpha_selector = page.query_selector('text="Alpha"')
    alpha_selector.click()
    time.sleep(0.5)

def select_project_ai_sdet360(page):
    # Select project 'AI.SDET360'
    project_selector = page.query_selector('text="Select Project"')
    project_selector.click()
    time.sleep(0.5)
    ai_sdet360_selector = page.query_selector('text="AI.SDET360"')
    ai_sdet360_selector.click()
    time.sleep(0.5)

def test_tc001(page):
    try:
        # Login
        page.goto('https://qa.sdet360.ai')
        username_selector = page.query_selector('input[name="email"]')
        username_selector.fill('neha.pal@sdettech.com')
        password_selector = page.query_selector('input[name="password"]')
        password_selector.fill('Neha@123')
        submit_button = page.query_selector('button[type="submit"]')
        submit_button.click()
        time.sleep(0.5)
        
        # Select vertical 'Alpha' and project 'AI.SDET360'
        select_vertical_alpha(page)
        select_project_ai_sdet360(page)
        
        # Verify that UI for 'Select vertical pop-up' menu should align with applications UI
        vertical_popup_selector = page.query_selector('mat-mdc-dialog-0')
        assert vertical_popup_selector.is_visible()
        _record('TC001 - Select Vertical pop-up', True)
    except Exception as e:
        _record('TC001 - Select Vertical pop-up', False, error=str(e))

def test_tc002(page):
    try:
        # Login
        page.goto('https://qa.sdet360.ai')
        username_selector = page.query_selector('input[name="email"]')
        username_selector.fill('neha.pal@sdettech.com')
        password_selector = page.query_selector('input[name="password"]')
        password_selector.fill('Neha@123')
        submit_button = page.query_selector('button[type="submit"]')
        submit_button.click()
        time.sleep(0.5)
        
        # Verify that dropdown arrow is appearing to the extreme right side of the tab
        vertical_popup_selector = page.query_selector('mat-mdc-dialog-0')
        assert vertical_popup_selector.is_visible()
        dropdown_arrow_selector = page.query_selector('text="Alpha"')
        assert dropdown_arrow_selector.is_visible()
        _record('TC002 - Dropdown arrow positioning', True)
    except Exception as e:
        _record('TC002 - Dropdown arrow positioning', False, error=str(e))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://qa.sdet360.ai')
    test_tc001(page)
    test_tc002(page)
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
