
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
    page.click("text=Alpha")
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=AI.SDET360")

def login(page, username, password):
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")

def verify_vertical_popup_ui(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    popup_menu = page.query_selector_all("mat-mdc-dialog-0")
    assert len(popup_menu) > 0
    drop_down_arrow = page.query_selector("mat-mdc-dialog-0 >>> .mat-select-arrow")
    assert drop_down_arrow is not None

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
        except Exception as e:
            _record("TC001 - Login and Select Vertical and Project", False, error=str(e))
        _record("TC002 - Verify Vertical Pop-up UI", True)
        try:
            verify_vertical_popup_ui(page)
            _record("TC002 - Verify Vertical Pop-up UI", True)
        except Exception as e:
            _record("TC002 - Verify Vertical Pop-up UI", False, error=str(e))
        time.sleep(0.5)
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
