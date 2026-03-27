
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
    vertical_selector = page.locator("select[name='vertical']")
    vertical_alpha_option = page.locator("option[value='463c42fd-f880-42b1-b609-cfb6faf156fe']")
    vertical_alpha_option.click()
    page.wait_for_selector("button:has-text('Submit')")
    page.locator("button:has-text('Submit')").click()

def select_project_ai_sdet360(page):
    project_selector = page.locator("select[name='project']")
    project_ai_sdet360_option = page.locator("option[value='d128c540-da8b-4487-b976-cf1c2a85bc3e']")
    project_ai_sdet360_option.click()
    page.wait_for_selector("button:has-text('Submit')")
    page.locator("button:has-text('Submit')").click()

def test_tc001():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            time.sleep(0.5)
            username_input = page.locator("input[name='email']")
            username_input.fill("neha.pal@sdettech.com")
            time.sleep(0.5)
            password_input = page.locator("input[name='password']")
            password_input.fill("Neha@123")
            time.sleep(0.5)
            submit_button = page.locator("button:has-text('Submit')")
            submit_button.click()
            time.sleep(0.5)
            select_vertical_alpha(page)
            time.sleep(0.5)
            select_project_ai_sdet360(page)
            time.sleep(0.5)
            _record("TC001 - Login and Select Vertical/Project", True)
    except Exception as e:
        _record("TC001 - Login and Select Vertical/Project", False, error=str(e))

def test_tc002():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            time.sleep(0.5)
            username_input = page.locator("input[name='email']")
            username_input.fill("neha.pal@sdettech.com")
            time.sleep(0.5)
            password_input = page.locator("input[name='password']")
            password_input.fill("Neha@123")
            time.sleep(0.5)
            submit_button = page.locator("button:has-text('Submit')")
            submit_button.click()
            time.sleep(0.5)
            select_vertical_alpha(page)
            time.sleep(0.5)
            project_selector = page.locator("select[name='project']")
            project_ai_sdet360_option = page.locator("option[value='d128c540-da8b-4487-b976-cf1c2a85bc3e']")
            project_ai_sdet360_option.hover()
            time.sleep(0.5)
            _record("TC002 - Hover Effect on Vertical/Project Selectors", True)
    except Exception as e:
        _record("TC002 - Hover Effect on Vertical/Project Selectors", False, error=str(e))

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
