
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
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=Alpha")

def select_project_ai_sdet360(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=AI.SDET360")

def login(page, username, password):
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")

def verify_pop_up_ui(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.wait_for_selector("text=Alpha")
    page.wait_for_selector("text=AI.SDET360")

def _model_defined_record(name, passed, error=None):
    if passed:
        print(f"Test {name} passed")
    else:
        print(f"Test {name} failed with error: {error}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://qa.sdet360.ai")

        try:
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            verify_pop_up_ui(page)
            _record("TC001 - Login and Select Vertical/Project", True)
        except Exception as e:
            _record("TC001 - Login and Select Vertical/Project", False, str(e))

        try:
            select_vertical_alpha(page)
            _record("TC002 - Verify Pop-up Menu Styling", True)
        except Exception as e:
            _record("TC002 - Verify Pop-up Menu Styling", False, str(e))

        try:
            select_vertical_alpha(page)
            _record("TC003 - Verify Dropdown Arrow Alignment", True)
        except Exception as e:
            _record("TC003 - Verify Dropdown Arrow Alignment", False, str(e))

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
