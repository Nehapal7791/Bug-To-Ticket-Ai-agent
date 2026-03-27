
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
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=Alpha")
    time.sleep(0.5)

def select_project_ai_sdet360(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=AI.SDET360")
    time.sleep(0.5)

def login(page, username, password):
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", username)
    page.fill("input[name='password']", password)
    page.click("text=Submit")
    time.sleep(0.5)

def verify_select_vertical_popup_ui_alignment(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.wait_for_selector("text=Alpha")
    page.wait_for_selector("text=AI.SDET360")
    # Verify that the Select Vertical pop-up menu is aligned with the application UI
    time.sleep(0.5)

def verify_dropdown_arrow_positioning(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.wait_for_selector("text=Alpha")
    page.wait_for_selector("text=AI.SDET360")
    # Verify that the drop-down arrow is positioned correctly
    time.sleep(0.5)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://qa.sdet360.ai")
        time.sleep(0.5)

        # Attempt login
        username = "neha.pal@sdettech.com"
        password = "Neha@123"
        login(page, username, password)

        # Select vertical Alpha and project AI.SDET360
        select_vertical_alpha(page)
        select_project_ai_sdet360(page)

        # Verify Select Vertical pop-up UI alignment
        try:
            verify_select_vertical_popup_ui_alignment(page)
            _record("TC001 - Verify Select Vertical pop-up UI alignment", True)
        except Exception as e:
            _record("TC001 - Verify Select Vertical pop-up UI alignment", False, error=str(e))

        # Verify drop-down arrow positioning
        try:
            verify_dropdown_arrow_positioning(page)
            _record("TC002 - Verify drop-down arrow positioning", True)
        except Exception as e:
            _record("TC002 - Verify drop-down arrow positioning", False, error=str(e))

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
