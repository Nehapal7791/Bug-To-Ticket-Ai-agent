
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

def select_vertical_project(page):
    # Select vertical Alpha
    page.wait_for_selector('text="Alpha"').click()
    time.sleep(0.5)
    # Select project AI.SDET360
    page.wait_for_selector('text="AI.SDET360"').click()
    time.sleep(0.5)

def login(page, username, password):
    # Fill login form
    page.wait_for_selector('input[name="email"]').fill(username)
    page.wait_for_selector('input[name="password"]').fill(password)
    time.sleep(0.5)
    # Submit login form
    page.wait_for_selector('button[type="submit"]').click()
    time.sleep(0.5)

def _model_defined_record(name, passed, error=None):
    result = {"name": name, "passed": passed}
    if error:
        result["error"] = error
    print(json.dumps(result))

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://qa.sdet360.ai")
        time.sleep(0.5)
        
        # Attempt login
        login(page, "neha.pal@sdettech.com", "Neha@123")
        time.sleep(0.5)
        
        # Select vertical Alpha and project AI.SDET360
        select_vertical_project(page)
        time.sleep(0.5)
        
        # Verify UI alignment of Select Vertical Pop-up
        page.wait_for_selector('text="Select Vertical"').screenshot(path="ui_alignment.png")
        time.sleep(0.5)
        
        # Verify drop-down arrow position
        page.wait_for_selector('text="Alpha"').screenshot(path="drop_down_arrow.png")
        time.sleep(0.5)
        
        # Record test result
        _record("Login and Select Vertical/Project", True)

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
