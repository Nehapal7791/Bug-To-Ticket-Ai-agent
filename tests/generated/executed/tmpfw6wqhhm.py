
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

def select_vertical_and_project(page):
    # Try text/role/label-based locators for visible UI
    vertical_select_locator = page.query_selector('text=Select Vertical')
    if vertical_select_locator:
        vertical_select_locator.click()
        page.wait_for_selector('text=Alpha')
        alpha_locator = page.query_selector('text=Alpha')
        if alpha_locator:
            alpha_locator.click()
    else:
        # If no DOM evidence for a selector exists, fail the test
        _record("Select Vertical and Project", False, error="No DOM evidence for Select Vertical selector")
        return

    project_select_locator = page.query_selector('text=Select Project')
    if project_select_locator:
        project_select_locator.click()
        page.wait_for_selector('text=AI.SDET360')
        ai_sdet360_locator = page.query_selector('text=AI.SDET360')
        if ai_sdet360_locator:
            ai_sdet360_locator.click()
    else:
        # If no DOM evidence for a selector exists, fail the test
        _record("Select Vertical and Project", False, error="No DOM evidence for Select Project selector")
        return

def login(page, username, password):
    # Start by navigating to the app and determining whether authentication is required
    page.goto("https://qa.sdet360.ai")
    time.sleep(0.5)

    # If a login form is present, locate the username/email input and password input dynamically
    login_form_locator = page.query_selector('text=Login')
    if login_form_locator:
        login_form_locator.click()
        time.sleep(0.5)
        username_input_locator = page.query_selector('name="email"')
        if username_input_locator:
            username_input_locator.fill(username)
            time.sleep(0.5)
            password_input_locator = page.query_selector('name="password"')
            if password_input_locator:
                password_input_locator.fill(password)
                time.sleep(0.5)
                submit_button_locator = page.query_selector('text=Submit')
                if submit_button_locator:
                    submit_button_locator.click()
                    time.sleep(0.5)
        else:
            # If no DOM evidence for a selector exists, fail the test
            _record("Login", False, error="No DOM evidence for username/email input selector")
            return
    else:
        # If no login form is present, continue with the rest of the test flow
        return

    # Wait for the post-login UI
    page.wait_for_selector('text=Authenticated Landing Page')
    time.sleep(0.5)

    # Select vertical and project
    select_vertical_and_project(page)

def test_app_crashes_when_opening_notifications_from_locked_screen(page, username, password):
    # Login to the app
    login(page, username, password)

    # Receive notification
    page.goto("https://qa.sdet360.ai/notifications")
    time.sleep(0.5)

    # Tap notification on locked screen
    page.click('text=Tap to open')
    time.sleep(0.5)

    # App crashes before opening
    page.wait_for_selector('text=App Crashed')

def _model_defined_record(name, success, error=None):
    result = {
        "test_name": name,
        "success": success,
        "error": error
    }
    print(json.dumps(result))
    sys.stdout.flush()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    username = "neha.pal@sdettech.com"
    password = "Neha@123"
    test_app_crashes_when_opening_notifications_from_locked_screen(page, username, password)
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
