
import json, sys, traceback
from pathlib import Path

_results = []
_errors  = []

def __cascade_record(name, passed, error=None, details=None):
    _results.append({{
        "name": name,
        "passed": passed,
        "error": error,
        "details": details or "",
    }})

_record = __cascade_record


import time
import json
import sys
from playwright.sync_api import sync_playwright

def select_vertical_and_project(page):
    page.wait_for_selector("#vertical-select")
    page.click("#vertical-select")
    page.wait_for_selector("#vertical-select > option:nth-child(2)")
    page.click("#vertical-select > option:nth-child(2)")
    page.wait_for_selector("#project-select")
    page.click("#project-select")
    page.wait_for_selector("#project-select > option:nth-child(2)")
    page.click("#project-select > option:nth-child(2)")

def login(page, username, password):
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", username)
    page.fill("input[name='password']", password)
    page.click("input[type='submit']")

def verify_pop_up(page):
    page.wait_for_selector("#pop-up-menu")
    pop_up_menu = page.query_selector("#pop-up-menu")
    assert pop_up_menu.get_attribute("style") == "background-color: #fff; border: 1px solid #ddd; padding: 10px;"

def test_TC001():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_and_project(page)
            verify_pop_up(page)
            _record("TC001 - Login and Select Vertical/Project", True)
    except Exception as e:
        _record("TC001 - Login and Select Vertical/Project", False, error=str(e))

def test_TC002():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_and_project(page)
            _record("TC002 - Verify Vertical/Project Selection Flow", True)
    except Exception as e:
        _record("TC002 - Verify Vertical/Project Selection Flow", False, error=str(e))

test_TC001()
test_TC002()


# ── Save results ──────────────────────────────────────────────
_output = {{
    "status": "PASS" if _results and all(r["passed"] for r in _results) else ("FAIL" if _results else "EXECUTION_ERROR"),
    "total": len(_results),
    "passed": sum(1 for r in _results if r["passed"]),
    "failed": sum(1 for r in _results if not r["passed"]),
    "tests": _results,
    "error": None if _results else "No tests were recorded by the generated script.",
}}
Path("reports/latest_run.json").write_text(json.dumps(_output, indent=2))
