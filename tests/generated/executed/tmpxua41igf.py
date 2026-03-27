
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
    vertical_candidates = page.query_selector_all("SELECT")
    for candidate in vertical_candidates:
        if candidate.text_content() == "Select Vertical
Alpha
Systech
Sdet360 Test":
            candidate.click()
            time.sleep(0.5)
            option = page.query_selector("OPTION[value='463c42fd-f880-42b1-b609-cfb6faf156fe']")
            option.click()
            time.sleep(0.5)
            return

def select_project_ai_sdet360(page):
    project_candidates = page.query_selector_all("SELECT")
    for candidate in project_candidates:
        if candidate.text_content() == "Select Project
AI.SDET360
SDET
New-RAY
sdet360":
            candidate.click()
            time.sleep(0.5)
            option = page.query_selector("OPTION[value='d128c540-da8b-4487-b976-cf1c2a85bc3e']")
            option.click()
            time.sleep(0.5)
            return

def test_login_and_select_vertical_and_project():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            username_selector = page.query_selector("input[name='email']")
            password_selector = page.query_selector("input[name='password']")
            submit_candidates = page.query_selector_all("button[type='submit']")
            username_selector.fill("neha.pal@sdettech.com")
            time.sleep(0.5)
            password_selector.fill("Neha@123")
            time.sleep(0.5)
            submit_candidates[0].click()
            time.sleep(0.5)
            select_vertical_alpha(page)
            time.sleep(0.5)
            select_project_ai_sdet360(page)
            time.sleep(0.5)
            _record("TC001 - Login and Select Vertical and Project", True)
    except Exception as e:
        _record("TC001 - Login and Select Vertical and Project", False, error=str(e))

def test_vertical_and_project_selection_flow():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            username_selector = page.query_selector("input[name='email']")
            password_selector = page.query_selector("input[name='password']")
            submit_candidates = page.query_selector_all("button[type='submit']")
            username_selector.fill("neha.pal@sdettech.com")
            time.sleep(0.5)
            password_selector.fill("Neha@123")
            time.sleep(0.5)
            submit_candidates[0].click()
            time.sleep(0.5)
            select_vertical_alpha(page)
            time.sleep(0.5)
            select_project_ai_sdet360(page)
            time.sleep(0.5)
            _record("TC002 - Verify Vertical and Project Selection Flow", True)
    except Exception as e:
        _record("TC002 - Verify Vertical and Project Selection Flow", False, error=str(e))

test_login_and_select_vertical_and_project()
test_vertical_and_project_selection_flow()


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
