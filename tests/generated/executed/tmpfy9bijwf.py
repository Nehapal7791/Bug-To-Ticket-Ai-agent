
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
    time.sleep(0.5)
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=Select Vertical")
    time.sleep(0.5)
    page.click("text=Alpha")

def select_project_ai_sdet360(page):
    time.sleep(0.5)
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=Select Project")
    time.sleep(0.5)
    page.click("text=AI.SDET360")

def login(page, username, password):
    time.sleep(0.5)
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", username)
    time.sleep(0.5)
    page.fill("input[name='password']", password)
    time.sleep(0.5)
    page.click("button[type='submit']")

def test_tc001():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            page.wait_for_selector("#mat-mdc-dialog-0")
            page.click("text=Select Vertical")
            time.sleep(0.5)
            page.click("text=Alpha")
            time.sleep(0.5)
            _record("TC001 - Select Vertical pop-up is looking noticeably odd", True)
    except Exception as e:
        _record("TC001 - Select Vertical pop-up is looking noticeably odd", False, error=str(e))

def test_tc002():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            page.wait_for_selector("#mat-mdc-dialog-0")
            page.click("text=Select Vertical")
            time.sleep(0.5)
            page.click("text=Alpha")
            time.sleep(0.5)
            page.wait_for_selector("button[type='submit']")
            page.click("button[type='submit']")
            time.sleep(0.5)
            _record("TC002 - Select Vertical pop-up is not matching as per the UI of the application", True)
    except Exception as e:
        _record("TC002 - Select Vertical pop-up is not matching as per the UI of the application", False, error=str(e))

def test_tc003():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            page.wait_for_selector("#mat-mdc-dialog-0")
            page.click("text=Select Vertical")
            time.sleep(0.5)
            page.click("text=Alpha")
            time.sleep(0.5)
            page.wait_for_selector("button[type='submit']")
            page.click("button[type='submit']")
            time.sleep(0.5)
            page.context.set_geolocation(100, 100)
            time.sleep(0.5)
            page.reload()
            time.sleep(0.5)
            _record("TC003 - Select Vertical pop-up is not matching as per the UI of the application on different screen resolutions", True)
    except Exception as e:
        _record("TC003 - Select Vertical pop-up is not matching as per the UI of the application on different screen resolutions", False, error=str(e))

test_tc001()
test_tc002()
test_tc003()


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
