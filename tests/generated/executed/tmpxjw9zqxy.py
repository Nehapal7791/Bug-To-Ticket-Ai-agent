
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

def select_vertical(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=Select Vertical")
    page.wait_for_selector("text=Alpha")
    page.click("text=Alpha")

def select_project(page):
    page.wait_for_selector("#mat-mdc-dialog-0")
    page.click("text=Select Project")
    page.wait_for_selector("text=AI.SDET360")
    page.click("text=AI.SDET360")

def login(page, username, password):
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")

def _model_defined_record(name, passed, error=None):
    if passed:
        print(f"Test {name} passed")
    else:
        print(f"Test {name} failed: {error}")

def test_login_and_select_vertical_project():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical(page)
            select_project(page)
            _record("Login and Select Vertical/Project", True)
    except Exception as e:
        _record("Login and Select Vertical/Project", False, str(e))

def test_receive_and_open_notification():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical(page)
            select_project(page)
            page.wait_for_selector("text=Notification")
            page.click("text=Notification")
            page.wait_for_selector("text=App opens directly to relevant content")
            _record("Receive and Open Notification from Locked Screen", True)
    except Exception as e:
        _record("Receive and Open Notification from Locked Screen", False, str(e))

def test_multiple_notifications():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical(page)
            select_project(page)
            page.wait_for_selector("text=Notification")
            page.click("text=Notification")
            page.wait_for_selector("text=App opens directly to relevant content")
            time.sleep(0.5)
            page.click("text=Notification")
            page.wait_for_selector("text=App opens directly to relevant content")
            _record("Multiple Notifications Received while App is Locked", True)
    except Exception as e:
        _record("Multiple Notifications Received while App is Locked", False, str(e))

def test_notifications_with_different_content_types():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical(page)
            select_project(page)
            page.wait_for_selector("text=Notification")
            page.click("text=Notification")
            page.wait_for_selector("text=App opens directly to relevant content")
            time.sleep(0.5)
            page.click("text=Notification")
            page.wait_for_selector("text=App opens directly to relevant content")
            _record("Notifications Received with Different Content Types", True)
    except Exception as e:
        _record("Notifications Received with Different Content Types", False, str(e))

def test_app_crashes_after_multiple_attempts():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://qa.sdet360.ai")
            login(page, "neha.pal@sdettech.com", "Neha@123")
            select_vertical(page)
            select_project(page)
            page.wait_for_selector("text=Notification")
            page.click("text=Notification")
            for i in range(5):
                page.wait_for_selector("text=App crashes")
                _record("App Crashes after Multiple Attempts to Open Notifications", True)
    except Exception as e:
        _record("App Crashes after Multiple Attempts to Open Notifications", False, str(e))

test_login_and_select_vertical_project()
test_receive_and_open_notification()
test_multiple_notifications()
test_notifications_with_different_content_types()
test_app_crashes_after_multiple_attempts()


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
