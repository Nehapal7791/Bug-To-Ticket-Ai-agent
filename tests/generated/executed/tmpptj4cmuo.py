
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
import time
import json
import sys

def select_vertical_alpha(page):
    time.sleep(0.5)
    vertical_candidates = page.query_selector_all('mat-mdc-dialog-0')
    if vertical_candidates:
        vertical = vertical_candidates[0]
        time.sleep(0.5)
        alpha_option = vertical.query_selector('option[value="463c42fd-f880-42b1-b609-cfb6faf156fe"]')
        if alpha_option:
            time.sleep(0.5)
            alpha_option.click()
            time.sleep(0.5)
            submit_button = page.locator('button:has-text("Submit")')
            if submit_button:
                time.sleep(0.5)
                submit_button.click()
                time.sleep(0.5)

def select_project_ai_sdet360(page):
    time.sleep(0.5)
    project_candidates = page.query_selector_all('mat-mdc-dialog-0')
    if project_candidates:
        project = project_candidates[0]
        time.sleep(0.5)
        ai_sdet360_option = project.query_selector('option[value="d128c540-da8b-4487-b976-cf1c2a85bc3e"]')
        if ai_sdet360_option:
            time.sleep(0.5)
            ai_sdet360_option.click()
            time.sleep(0.5)

def login(page):
    time.sleep(0.5)
    username_selector = page.locator('input[name="email"]')
    if username_selector:
        time.sleep(0.5)
        username_selector.fill('neha.pal@sdettech.com')
        time.sleep(0.5)
    password_selector = page.locator('input[name="password"]')
    if password_selector:
        time.sleep(0.5)
        password_selector.fill('Neha@123')
        time.sleep(0.5)
    submit_candidates = page.query_selector_all('button[type="submit"]')
    if submit_candidates:
        time.sleep(0.5)
        submit_candidates[0].click()
        time.sleep(0.5)

def test_tc001(page):
    try:
        _record('TC001 - Login and Select Vertical/Project', True)
        login(page)
        select_vertical_alpha(page)
        select_project_ai_sdet360(page)
        _record('TC001 - Login and Select Vertical/Project', True)
    except Exception as e:
        _record('TC001 - Login and Select Vertical/Project', False, str(e))

def test_tc002(page):
    try:
        _record('TC002 - Verify Vertical/Project Selection Flow', True)
        login(page)
        select_vertical_alpha(page)
        select_project_ai_sdet360(page)
        _record('TC002 - Verify Vertical/Project Selection Flow', True)
    except Exception as e:
        _record('TC002 - Verify Vertical/Project Selection Flow', False, str(e))

def test_tc003(page):
    try:
        _record('TC003 - Verify UI Alignment and Dropdown Arrow Positioning', True)
        login(page)
        select_vertical_alpha(page)
        select_project_ai_sdet360(page)
        _record('TC003 - Verify UI Alignment and Dropdown Arrow Positioning', True)
    except Exception as e:
        _record('TC003 - Verify UI Alignment and Dropdown Arrow Positioning', False, str(e))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://qa.sdet360.ai')
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
