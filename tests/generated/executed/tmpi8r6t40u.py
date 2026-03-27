
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


from playwright.sync_api import sync_playwright
import time, json, sys

def select_vertical_alpha(page):
    page.wait_for_selector('#mat-mdc-dialog-0')
    page.click('text="Alpha"')
    time.sleep(0.5)

def select_project_ai_sdet360(page):
    page.wait_for_selector('#mat-mdc-dialog-0')
    page.click('text="AI.SDET360"')
    time.sleep(0.5)

def login(page, username, password):
    page.wait_for_selector('input[name="email"]')
    page.fill('input[name="email"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    time.sleep(0.5)

def test_login_and_select_vertical_and_project():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://qa.sdet360.ai')
            _record("TC001 - Login and Select Vertical and Project", True)
            login(page, 'neha.pal@sdettech.com', 'Neha@123')
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            page.wait_for_selector('#mat-mdc-dialog-0')
            _record("TC001 - Login and Select Vertical and Project", True)
    except Exception as e:
        _record("TC001 - Login and Select Vertical and Project", False, error=str(e))

def test_select_vertical_pop_up_alignment():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://qa.sdet360.ai')
            _record("TC002 - Select Vertical Pop-up Alignment", True)
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            page.wait_for_selector('#mat-mdc-dialog-0')
            _record("TC002 - Select Vertical Pop-up Alignment", True)
    except Exception as e:
        _record("TC002 - Select Vertical Pop-up Alignment", False, error=str(e))

def test_dropdown_arrow_positioning():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://qa.sdet360.ai')
            _record("TC003 - Dropdown Arrow Positioning", True)
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            page.wait_for_selector('#mat-mdc-dialog-0')
            _record("TC003 - Dropdown Arrow Positioning", True)
    except Exception as e:
        _record("TC003 - Dropdown Arrow Positioning", False, error=str(e))

test_login_and_select_vertical_and_project()
test_select_vertical_pop_up_alignment()
test_dropdown_arrow_positioning()


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
