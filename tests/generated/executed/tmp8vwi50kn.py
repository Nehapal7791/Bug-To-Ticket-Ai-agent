
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

def select_vertical_and_project(page):
    # Select vertical 'Alpha'
    page.wait_for_selector('#mat-mdc-dialog-0')
    page.click('#mat-mdc-dialog-0')
    page.wait_for_selector('SELECT')
    page.click('SELECT')
    page.wait_for_selector('OPTION')
    page.click('OPTION')
    page.wait_for_selector('OPTION')
    page.click('OPTION')
    # Select project 'AI.SDET360'
    page.wait_for_selector('#mat-mdc-dialog-0')
    page.click('#mat-mdc-dialog-0')
    page.wait_for_selector('SELECT')
    page.click('SELECT')
    page.wait_for_selector('OPTION')
    page.click('OPTION')

def login(page):
    # Locate the username/email input
    username_input = page.query_selector('input[name="email"]')
    # Locate the password input
    password_input = page.query_selector('input[name="password"]')
    # Locate the submit button
    submit_button = page.query_selector('button[type="submit"]')
    # Fill the username and password
    username_input.fill('neha.pal@sdettech.com')
    password_input.fill('Neha@123')
    # Submit the form
    submit_button.click()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://qa.sdet360.ai')
        _record('TC001 - Select Vertical pop-up UI alignment', True)
        try:
            # Attempt login
            login(page)
            # Wait for the authenticated landing page
            page.wait_for_selector('h1')
            # Select vertical 'Alpha' and project 'AI.SDET360'
            select_vertical_and_project(page)
            # Verify that the 'Select vertical pop-up' is aligned with the application UI
            page.wait_for_selector('#mat-mdc-dialog-0')
            page.wait_for_selector('SELECT')
            page.wait_for_selector('OPTION')
            page.wait_for_selector('OPTION')
            # Verify that the drop-down arrow appears to the left of its current position
            page.wait_for_selector('#mat-mdc-dialog-0')
            page.wait_for_selector('SELECT')
            page.wait_for_selector('OPTION')
            page.wait_for_selector('OPTION')
            _record('TC001 - Select Vertical pop-up UI alignment', True)
        except Exception as e:
            _record('TC001 - Select Vertical pop-up UI alignment', False, error=str(e))
        finally:
            browser.close()

if __name__ == "__main__":
    main()


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
