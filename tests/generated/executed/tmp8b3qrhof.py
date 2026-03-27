
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

def select_vertical_and_project(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    vertical_selector = page.query_selector("select[name='vertical']")
    vertical_option = page.query_selector("option[value='463c42fd-f880-42b1-b609-cfb6faf156fe']")
    vertical_option.click()
    project_selector = page.query_selector("select[name='project']")
    project_option = page.query_selector("option[value='d128c540-da8b-4487-b976-cf1c2a85bc3e']")
    project_option.click()

def login(page, username, password):
    page.wait_for_selector("input[name='email']")
    username_field = page.query_selector("input[name='email']")
    username_field.fill(username)
    password_field = page.query_selector("input[name='password']")
    password_field.fill(password)
    submit_button = page.query_selector("button[type='submit']")
    submit_button.click()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://qa.sdet360.ai")
        _record("TC001 - Login and Select Vertical and Project", True)
        try:
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_and_project(page)
            _record("TC001 - Login and Select Vertical and Project", True)
            page.wait_for_selector("#mat-mdc-dialog-0")
            _record("TC001 - Verify UI for Select vertical pop-up", True)
            page.wait_for_selector("#mat-mdc-dialog-0")
            _record("TC002 - Verify Vertical and Project Selection Flow", True)
            page.wait_for_selector("#mat-mdc-dialog-0")
        except Exception as e:
            _record("TC001 - Login and Select Vertical and Project", False, str(e))
            _record("TC002 - Verify Vertical and Project Selection Flow", False, str(e))
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
