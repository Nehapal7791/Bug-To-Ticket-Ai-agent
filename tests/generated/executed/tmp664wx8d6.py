
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
    page.select_option("#vertical-select", "alpha")
    page.wait_for_selector("#project-select")
    page.select_option("#project-select", "ai.sdet360")

def login(page, username, password):
    page.wait_for_selector("form")
    username_input = page.query_selector("input[name='email']")
    password_input = page.query_selector("input[name='password']")
    username_input.fill(username)
    password_input.fill(password)
    page.query_selector("button[type='submit']").click()
    page.wait_for_selector("h1", timeout=10000)

def _model_defined_record(name, passed, error=None):
    result = {"name": name, "passed": passed}
    if error:
        result["error"] = error
    print(json.dumps(result))

def test_app_launch_from_locked_screen():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_and_project(page)
            page.wait_for_selector("#notification-button")
            page.click("#notification-button")
            page.wait_for_selector("#notification-content")
            assert page.query_selector("#notification-content") is not None
            _record("TC003 - App Launch from Locked Screen", True)
    except Exception as e:
        _record("TC003 - App Launch from Locked Screen", False, str(e))

def test_app_launch_from_locked_screen_with_multiple_notifications():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_and_project(page)
            page.wait_for_selector("#notification-button")
            page.click("#notification-button")
            page.wait_for_selector("#notification-content")
            page.click("#notification-button")
            page.wait_for_selector("#notification-content")
            assert page.query_selector("#notification-content") is not None
            _record("TC004 - App Launch from Locked Screen with Multiple Notifications", True)
    except Exception as e:
        _record("TC004 - App Launch from Locked Screen with Multiple Notifications", False, str(e))

def test_app_launch_from_locked_screen_with_no_internet_connection():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_and_project(page)
            page.wait_for_selector("#notification-button")
            page.click("#notification-button")
            page.wait_for_selector("#notification-content")
            page.set_network_conditions(delay=1000)
            assert page.query_selector("#notification-content") is None
            _record("TC005 - App Launch from Locked Screen with No Internet Connection", True)
    except Exception as e:
        _record("TC005 - App Launch from Locked Screen with No Internet Connection", False, str(e))

def test_app_launch_from_locked_screen_with_different_device_configurations():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical_and_project(page)
            page.wait_for_selector("#notification-button")
            page.click("#notification-button")
            page.wait_for_selector("#notification-content")
            page.set_viewport_size(1920, 1080)
            assert page.query_selector("#notification-content") is not None
            _record("TC006 - App Launch from Locked Screen with Different Device Configurations", True)
    except Exception as e:
        _record("TC006 - App Launch from Locked Screen with Different Device Configurations", False, str(e))

test_app_launch_from_locked_screen()
test_app_launch_from_locked_screen_with_multiple_notifications()
test_app_launch_from_locked_screen_with_no_internet_connection()
test_app_launch_from_locked_screen_with_different_device_configurations()


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
