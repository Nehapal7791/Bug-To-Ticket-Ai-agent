
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

# Define reusable helper for selecting vertical Alpha and project AI.SDET360
def select_vertical_and_project(page):
    # Wait for the vertical and project dropdowns to be visible
    page.wait_for_selector("#mat-mdc-dialog-0")
    # Select vertical Alpha
    page.wait_for_selector("SELECT[id='']", timeout=10000)
    page.select_option("SELECT[id='']", "Alpha")
    # Select project AI.SDET360
    page.wait_for_selector("SELECT[id='']", timeout=10000)
    page.select_option("SELECT[id='']", "AI.SDET360")

# Define test TC001
def test_tc001():
    try:
        # Create a new browser instance
        browser = sync_playwright().start()
        # Create a new page instance
        page = browser.new_page()
        # Navigate to the application url
        page.goto("https://qa.sdet360.ai")
        # Wait for the login form to be visible
        page.wait_for_selector("input[name='email']")
        # Fill in the login credentials
        page.fill("input[name='email']", "neha.pal@sdettech.com")
        page.fill("input[name='password']", "Neha@123")
        # Submit the login form
        page.click("button[type='submit']")
        # Wait for the login to be successful
        page.wait_for_selector("#mat-mdc-dialog-0")
        # Select vertical Alpha and project AI.SDET360
        select_vertical_and_project(page)
        # Verify that the 'Select Vertical pop-up' is not matching as per the UI of our application
        page.wait_for_selector("#mat-mdc-dialog-0")
        page.screenshot(path="screenshot.png")
        # Record the test result
        _record("TC001 - Login and Select Vertical and Project", True)
    except Exception as e:
        # Record the test result with error
        _record("TC001 - Login and Select Vertical and Project", False, error=str(e))

# Define test TC002
def test_tc002():
    try:
        # Create a new browser instance
        browser = sync_playwright().start()
        # Create a new page instance
        page = browser.new_page()
        # Navigate to the application url
        page.goto("https://qa.sdet360.ai")
        # Wait for the login form to be visible
        page.wait_for_selector("input[name='email']")
        # Fill in the login credentials
        page.fill("input[name='email']", "neha.pal@sdettech.com")
        page.fill("input[name='password']", "Neha@123")
        # Submit the login form
        page.click("button[type='submit']")
        # Wait for the login to be successful
        page.wait_for_selector("#mat-mdc-dialog-0")
        # Select vertical Alpha and project AI.SDET360
        select_vertical_and_project(page)
        # Verify that the vertical and project are selected successfully
        page.wait_for_selector("#mat-mdc-dialog-0")
        # Record the test result
        _record("TC002 - Select Vertical and Project", True)
    except Exception as e:
        # Record the test result with error
        _record("TC002 - Select Vertical and Project", False, error=str(e))

# Run the tests
test_tc001()
test_tc002()


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
