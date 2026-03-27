import time
import json
import sys
from playwright.sync_api import sync_playwright

# ── Result recorder ───────────────────────────────────────────────────────────
results = []

def _record(name, passed, error=""):
    results.append({"name": name, "passed": passed, "error": error})
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name}" + (f"\n     Error: {error}" if error else ""))


# ── Helpers ───────────────────────────────────────────────────────────────────
def login(page):
    page.goto("https://qa.sdet360.ai")
    page.wait_for_selector("input[name='email']")
    page.fill("input[name='email']", "neha.pal@sdettech.com")
    time.sleep(0.5)
    page.fill("input[name='password']", "Neha@123")
    time.sleep(0.5)
    page.click("button[type='submit']")
 
    page.wait_for_selector("mat-dialog-container", timeout=15000)
    time.sleep(1)


def select_vertical_alpha(page):
    vertical_dropdown = page.locator("mat-dialog-container select").nth(0)
    vertical_dropdown.wait_for(state="visible", timeout=10000)
    vertical_dropdown.select_option(value="463c42fd-f880-42b1-b609-cfb6faf156fe")
    time.sleep(0.5)


def select_project_ai_sdet360(page): 
    project_dropdown = page.locator("mat-dialog-container select").nth(1)
    project_dropdown.wait_for(state="visible", timeout=10000)
    project_dropdown.select_option(value="d128c540-da8b-4487-b976-cf1c2a85bc3e")
    time.sleep(0.5)


def submit_and_enter_app(page): 
    page.locator("mat-dialog-container button:has-text('Submit')").click()
    page.wait_for_selector("mat-dialog-container", state="hidden", timeout=15000)
    print(f"  → Entered app. Current URL: {page.url}")


# ── TC001 ─────────────────────────────────────────────────────────────────────
def test_login_and_select_vertical_and_project():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()

            login(page)
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            submit_and_enter_app(page)

            page.screenshot(path="screenshot_tc001.png")
            _record("TC001 - Login and Select Vertical and Project", True)

            time.sleep(2)  
            browser.close()

    except Exception as e:
        _record("TC001 - Login and Select Vertical and Project", False, error=str(e))


def test_vertical_and_project_selection_flow():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()

            login(page)
            select_vertical_alpha(page)
            select_project_ai_sdet360(page)
            submit_and_enter_app(page)

            # ✅ Verify dialog is gone = we're inside the app
            assert page.locator("mat-dialog-container").count() == 0, \
                "Dialog still visible — vertical/project selection failed"

            page.screenshot(path="screenshot_tc002.png")
            _record("TC002 - Verify Vertical and Project Selection Flow", True)

            time.sleep(2)
            browser.close()

    except Exception as e:
        _record("TC002 - Verify Vertical and Project Selection Flow", False, error=str(e))


test_login_and_select_vertical_and_project()
test_vertical_and_project_selection_flow()

print("\n── Test Summary ──────────────────────────────")
for r in results:
    status = "✅ PASS" if r["passed"] else "❌ FAIL"
    print(f"{status}  {r['name']}" + (f"\n     Error: {r['error']}" if r["error"] else ""))

passed = sum(1 for r in results if r["passed"])
print(f"\nTotal: {passed}/{len(results)} passed")