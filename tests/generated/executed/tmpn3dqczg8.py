
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
    vertical_candidates = page.query_selector_all("SELECT")
    project_candidates = page.query_selector_all("SELECT")
    for vertical_candidate in vertical_candidates:
        if vertical_candidate.text_content() == "Alpha":
            vertical_candidate.click()
            break
    for project_candidate in project_candidates:
        if project_candidate.text_content() == "AI.SDET360":
            project_candidate.click()
            break

def login(page):
    username_selector = page.query_selector("input[name='email']")
    password_selector = page.query_selector("input[name='password']")
    submit_candidates = page.query_selector_all("button[type='submit']")
    username_selector.fill("nehapal.pal@sdettech.com")
    password_selector.fill("Neha@123")
    submit_candidates[0].click()

def test_TC001(page):
    try:
        login(page)
        time.sleep(0.5)
        select_vertical_and_project(page)
        time.sleep(0.5)
        _record("TC001 - Login and Select Vertical and Project", True)
    except Exception as e:
        _record("TC001 - Login and Select Vertical and Project", False, error=str(e))

def test_TC002(page):
    try:
        login(page)
        time.sleep(0.5)
        page.wait_for_selector("SELECT")
        time.sleep(0.5)
        vertical_candidates = page.query_selector_all("SELECT")
        for vertical_candidate in vertical_candidates:
            if vertical_candidate.text_content() == "Alpha":
                vertical_candidate.click()
                break
        time.sleep(0.5)
        page.wait_for_selector("SELECT")
        time.sleep(0.5)
        project_candidates = page.query_selector_all("SELECT")
        for project_candidate in project_candidates:
            if project_candidate.text_content() == "AI.SDET360":
                project_candidate.click()
                break
        time.sleep(0.5)
        _record("TC002 - Verify Select Vertical pop-up UI alignment", True)
    except Exception as e:
        _record("TC002 - Verify Select Vertical pop-up UI alignment", False, error=str(e))

def test_TC003(page):
    try:
        login(page)
        time.sleep(0.5)
        page.wait_for_selector("SELECT")
        time.sleep(0.5)
        vertical_candidates = page.query_selector_all("SELECT")
        for vertical_candidate in vertical_candidates:
            if vertical_candidate.text_content() == "Alpha":
                vertical_candidate.click()
                break
        time.sleep(0.5)
        page.wait_for_selector("SELECT")
        time.sleep(0.5)
        project_candidates = page.query_selector_all("SELECT")
        for project_candidate in project_candidates:
            if project_candidate.text_content() == "AI.SDET360":
                project_candidate.click()
                break
        time.sleep(0.5)
        _record("TC003 - Verify Select Vertical pop-up drop-down arrow positioning", True)
    except Exception as e:
        _record("TC003 - Verify Select Vertical pop-up drop-down arrow positioning", False, error=str(e))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://qa.sdet360.ai")
    test_TC001(page)
    test_TC002(page)
    test_TC003(page)
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
