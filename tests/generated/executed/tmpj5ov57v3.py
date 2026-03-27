
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
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=Select Vertical and Project")
    page.wait_for_selector("text=Alpha")
    page.click("text=Alpha")
    page.wait_for_selector("text=AI.SDET360")
    page.click("text=AI.SDET360")

def login(page, username, password):
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", username)
    page.fill("input[name='password']", password)
    page.wait_for_selector("button[type='submit']")
    page.click("button[type='submit']")

def _model_defined_record(name, passed, error=None):
    result = {"name": name, "passed": passed}
    if error:
        result["error"] = error
    print(json.dumps(result))

def test_login():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            _record("TC001 - Login to App", True)
    except Exception as e:
        _record("TC001 - Login to App", False, str(e))

def test_select_vertical_and_project():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            select_vertical_and_project(page)
            _record("TC002 - Select Vertical and Project", True)
    except Exception as e:
        _record("TC002 - Select Vertical and Project", False, str(e))

def test_app_crashes_when_opening_notifications_from_locked_screen():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            select_vertical_and_project(page)
            page.wait_for_selector("input[name='email']")
            page.fill("input[name='email']", "neha.pal@sdettech.com")
            page.fill("input[name='password']", "Neha@123")
            page.click("button[type='submit']")
            page.wait_for_selector("text=Alpha")
            page.click("text=Alpha")
            page.wait_for_selector("text=AI.SDET360")
            page.click("text=AI.SDET360")
            time.sleep(0.5)
            page.click("text=Receive notification")
            time.sleep(0.5)
            page.click("text=Tap notification on locked screen")
            time.sleep(0.5)
            _record("TC003 - App crashes when opening notifications from locked screen", True)
    except Exception as e:
        _record("TC003 - App crashes when opening notifications from locked screen", False, str(e))

test_login()
test_select_vertical_and_project()
test_app_crashes_when_opening_notifications_from_locked_screen()


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
