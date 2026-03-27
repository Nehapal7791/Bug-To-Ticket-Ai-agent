
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

def select_vertical_alpha(page):
    vertical_candidates = page.query_selector_all('SELECT[id="mat-mdc-dialog-0"]')
    vertical_alpha_option = vertical_candidates[0].query_selector('OPTION[value="463c42fd-f880-42b1-b609-cfb6faf156fe"]')
    vertical_alpha_option.click()
    time.sleep(0.5)

def select_project_ai_sdet360(page):
    project_candidates = page.query_selector_all('SELECT[id="mat-mdc-dialog-0"]')
    project_ai_sdet360_option = project_candidates[0].query_selector('OPTION[value="d128c540-da8b-4487-b976-cf1c2a85bc3e"]')
    project_ai_sdet360_option.click()
    time.sleep(0.5)

def login(page):
    username_selector = page.query_selector('input[name="email"]')
    username_selector.fill('neha.pal@sdettech.com')
    time.sleep(0.5)
    password_selector = page.query_selector('input[name="password"]')
    password_selector.fill('Neha@123')
    time.sleep(0.5)
    submit_button = page.query_selector('button[type="submit"]')
    submit_button.click()
    time.sleep(0.5)

def verify_select_vertical_pop_up_ui(page):
    select_vertical_alpha(page)
    select_project_ai_sdet360(page)
    time.sleep(0.5)
    pop_up_menu = page.query_selector('MAT-DIALOG-CONTAINER[id="mat-mdc-dialog-0"]')
    assert pop_up_menu.is_visible()
    time.sleep(0.5)
    drop_down_arrow = pop_up_menu.query_selector('SELECT[id="mat-mdc-dialog-0"]')
    assert drop_down_arrow.is_visible()

def _model_defined_record(name, passed, error=None):
    if passed:
        print(f"Test {name} passed")
    else:
        print(f"Test {name} failed with error: {error}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://qa.sdet360.ai')
        time.sleep(0.5)
        login(page)
        time.sleep(0.5)
        verify_select_vertical_pop_up_ui(page)
        time.sleep(0.5)
        browser.close()

try:
    main()
except Exception as e:
    _record('TC002 - Verify Select Vertical Pop-up UI', False, str(e))


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
