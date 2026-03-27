
import json, sys, traceback
from pathlib import Path

_results = []
_errors  = []

def __cascade_record(name, passed, error=None, details=None):
    _results.append({{
        "name": name,
        "passed": passed,
        "error": error,
        "details": details or "",
    }})

_record = __cascade_record


import time
import json
import sys
from playwright.sync_api import sync_playwright

def select_vertical_and_project(page):
    # Select vertical Alpha
    page.wait_for_selector('#vertical-select')
    page.select_option('#vertical-select', 'Alpha')
    time.sleep(0.5)
    # Select project AI.SDET360
    page.wait_for_selector('#project-select')
    page.select_option('#project-select', 'AI.SDET360')
    time.sleep(0.5)

def login(page, username, password):
    # Determine if authentication is required
    if page.query_selector('input[name="email"]'):
        # Fill in the provided username and password
        page.wait_for_selector('input[name="email"]')
        page.fill('input[name="email"]', username)
        page.fill('input[name="password"]', password)
        time.sleep(0.5)
        # Submit the login form
        page.wait_for_selector('button[type="submit"]')
        page.click('button[type="submit"]')
        time.sleep(0.5)
    else:
        print("No login form found")

def _model_defined_record(name, passed, error=None):
    # Record test result
    if passed:
        print(f"{name} passed")
    else:
        print(f"{name} failed")
        if error:
            print(f"Error: {error}")

def test_app_crashes_when_opening_notifications_from_locked_screen():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://qa.sdet360.ai')
            login(page, 'neha.pal@sdettech.com', 'Neha@123')
            select_vertical_and_project(page)
            # Receive notification
            page.wait_for_selector('.notification')
            page.click('.notification')
            time.sleep(0.5)
            # Tap notification on locked screen
            page.wait_for_selector('.locked-screen-notification')
            page.click('.locked-screen-notification')
            time.sleep(0.5)
            # Check if app crashes
            if page.query_selector('.crashed-app'):
                _record('TC003 - App crashes when opening notifications from locked screen', False, "App crashed")
            else:
                _record('TC003 - App crashes when opening notifications from locked screen', True)
    except Exception as e:
        _record('TC003 - App crashes when opening notifications from locked screen', False, str(e))

test_app_crashes_when_opening_notifications_from_locked_screen()


# ── Save results ──────────────────────────────────────────────
_output = {{
    "status": "PASS" if _results and all(r["passed"] for r in _results) else ("FAIL" if _results else "EXECUTION_ERROR"),
    "total": len(_results),
    "passed": sum(1 for r in _results if r["passed"]),
    "failed": sum(1 for r in _results if not r["passed"]),
    "tests": _results,
    "error": None if _results else "No tests were recorded by the generated script.",
}}
Path("reports/latest_run.json").write_text(json.dumps(_output, indent=2))
