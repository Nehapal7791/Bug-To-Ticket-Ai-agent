import json
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from config import APP_PROJECT_NAME, APP_VERTICAL_NAME
from tools.playwright_runner import _run_python_script

INSPECTION_DIR = Path("reports/inspection")

try:
    from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
    from langchain_community.tools.playwright import ClickTool
    from langchain_community.tools.playwright import CurrentWebPageTool
    from langchain_community.tools.playwright import ExtractTextTool
    from langchain_community.tools.playwright import GetElementsTool
    from langchain_community.tools.playwright import NavigateTool
    from langchain_community.tools.playwright.utils import create_async_playwright_browser

    HAS_LANGCHAIN_PLAYWRIGHT = True
except Exception:
    PlayWrightBrowserToolkit = None
    ClickTool = None
    CurrentWebPageTool = None
    ExtractTextTool = None
    GetElementsTool = None
    NavigateTool = None
    create_async_playwright_browser = None
    HAS_LANGCHAIN_PLAYWRIGHT = False


def _build_generic_summary(
    *,
    url: str,
    vertical: str,
    project: str,
    backend: str,
    username: str | None,
    password: str | None,
) -> dict:
    return {
        "backend": backend,
        "login_detected": False,
        "login_attempted": False,
        "login_success_likely": False,
        "current_url": url,
        "vertical_name": vertical,
        "project_name": project,
        "username_selector": None,
        "password_selector": None,
        "submit_candidates": [],
        "vertical_candidates": [],
        "project_candidates": [],
        "elements_before_login": [],
        "elements_after_login": [],
        "visible_text_excerpt": "",
        "notes": [
            "Inspection is designed to be general-purpose across arbitrary websites.",
            f"Credentials supplied={bool(username and password)}",
        ],
    }


def _inspect_with_langchain_toolkit(
    url: str,
    username: str | None,
    password: str | None,
    vertical: str,
    project: str,
) -> dict:
    script = dedent(
        f'''
        import asyncio
        import json
        from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
        from langchain_community.tools.playwright import ClickTool
        from langchain_community.tools.playwright import CurrentWebPageTool
        from langchain_community.tools.playwright import ExtractTextTool
        from langchain_community.tools.playwright import GetElementsTool
        from langchain_community.tools.playwright import NavigateTool
        from langchain_community.tools.playwright.utils import create_async_playwright_browser

        URL = {url!r}
        USERNAME = {username!r}
        PASSWORD = {password!r}
        VERTICAL = {vertical!r}
        PROJECT = {project!r}

        async def main():
            async_browser = create_async_playwright_browser(headless=True)
            toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
            _ = toolkit.get_tools()

            navigate_tool = NavigateTool(async_browser=async_browser)
            current_page_tool = CurrentWebPageTool(async_browser=async_browser)
            extract_text_tool = ExtractTextTool(async_browser=async_browser)
            get_elements_tool = GetElementsTool(async_browser=async_browser)
            click_tool = ClickTool(async_browser=async_browser, visible_only=False)

            summary = {repr(_build_generic_summary(url=url, vertical=vertical, project=project, backend="langchain_playwright_toolkit", username=username, password=password))}

            await navigate_tool.ainvoke({{"url": URL}})
            summary["current_url"] = await current_page_tool.ainvoke({{}})

            try:
                summary["visible_text_excerpt"] = (await extract_text_tool.ainvoke({{}}))[:4000]
            except Exception as exc:
                summary["notes"].append(f"ExtractTextTool failed: {{exc}}")

            selector_groups = {{
                "elements_before_login": "button, input, a, select, textarea, option, label, [role], [data-testid], [placeholder]",
                "vertical_candidates": "*:has-text('" + VERTICAL.replace("'", "") + "')",
                "project_candidates": "*:has-text('" + PROJECT.replace("'", "") + "')",
                "username_candidates": "input[type='email'], input[name*='user'], input[name*='email'], input[placeholder*='email' i], input[placeholder*='user' i]",
                "password_candidates": "input[type='password'], input[name*='password'], input[placeholder*='password' i]",
                "submit_candidates": "button[type='submit'], input[type='submit'], button, [role='button']",
            }}

            for key, selector in selector_groups.items():
                try:
                    data = await get_elements_tool.ainvoke({{
                        "selector": selector,
                        "attributes": ["innerText", "outerHTML", "name", "type", "placeholder", "id", "value", "data-testid", "role"],
                    }})
                except Exception as exc:
                    summary["notes"].append(f"GetElementsTool failed for {{key}}: {{exc}}")
                    data = []

                if key == "username_candidates":
                    if data:
                        summary["login_detected"] = True
                        summary["username_selector"] = selector
                elif key == "password_candidates":
                    if data:
                        summary["login_detected"] = True
                        summary["password_selector"] = selector
                elif key == "submit_candidates":
                    summary["submit_candidates"] = data[:10] if isinstance(data, list) else [data]
                else:
                    summary[key] = data[:25] if isinstance(data, list) else [data]

            if USERNAME and PASSWORD and summary["login_detected"]:
                summary["login_attempted"] = True
                summary["notes"].append("LangChain toolkit backend detected login fields; final credential entry is deferred to generated execution script.")

            try:
                if isinstance(summary["vertical_candidates"], list) and not summary["vertical_candidates"]:
                    await click_tool.ainvoke({{"selector": "text=Select vertical"}})
                    refreshed = await get_elements_tool.ainvoke({{
                        "selector": "*:has-text('" + VERTICAL.replace("'", "") + "')",
                        "attributes": ["innerText", "outerHTML"],
                    }})
                    summary["vertical_candidates"] = refreshed[:25] if isinstance(refreshed, list) else [refreshed]
            except Exception:
                pass

            summary["elements_after_login"] = summary["elements_before_login"]
            print(json.dumps(summary))

        asyncio.run(main())
        '''
    )

    result = _run_python_script(script, timeout=60)
    output = result.get("stdout", "").strip()
    if result.get("returncode"):
        raise RuntimeError(result.get("stderr", "LangChain toolkit inspection failed"))
    return json.loads(output)


def _inspect_with_raw_playwright(
    url: str,
    username: str | None,
    password: str | None,
    vertical: str,
    project: str,
) -> dict:
    summary = _build_generic_summary(
        url=url,
        vertical=vertical,
        project=project,
        backend="raw_playwright_fallback",
        username=username,
        password=password,
    )
    summary["notes"].append("LangChain PlayWrightBrowserToolkit not available; using raw Playwright fallback.")
    return summary


def inspect_application(
    url: str,
    username: str | None = None,
    password: str | None = None,
    vertical_name: str | None = None,
    project_name: str | None = None,
) -> dict:
    vertical = vertical_name or APP_VERTICAL_NAME
    project = project_name or APP_PROJECT_NAME
    INSPECTION_DIR.mkdir(parents=True, exist_ok=True)

    if HAS_LANGCHAIN_PLAYWRIGHT:
        try:
            inspection = _inspect_with_langchain_toolkit(url, username, password, vertical, project)
        except Exception as exc:
            inspection = _inspect_with_raw_playwright(url, username, password, vertical, project)
            inspection["notes"].append(f"Toolkit inspection failed and fell back to raw Playwright: {exc}")
    else:
        inspection = _inspect_with_raw_playwright(url, username, password, vertical, project)

    script = dedent(
        f'''
        import json
        from playwright.sync_api import sync_playwright

        URL = {url!r}
        USERNAME = {username!r}
        PASSWORD = {password!r}
        VERTICAL = {vertical!r}
        PROJECT = {project!r}

        def collect_elements(page):
            return page.evaluate("""() => {{
                const selectors = 'button, input, a, select, textarea, option, [role], [data-testid], [placeholder], label';
                const els = Array.from(document.querySelectorAll(selectors)).slice(0, 200);
                return els.map((el) => {{
                    const rect = el.getBoundingClientRect();
                    return {{
                        tag: el.tagName,
                        id: el.id || '',
                        name: el.getAttribute('name') || '',
                        type: el.getAttribute('type') || '',
                        text: (el.innerText || el.textContent || '').trim().slice(0, 120),
                        placeholder: el.getAttribute('placeholder') || '',
                        testId: el.getAttribute('data-testid') || '',
                        role: el.getAttribute('role') || '',
                        ariaLabel: el.getAttribute('aria-label') || '',
                        value: (el.value || '').toString().slice(0, 80),
                        visible: !!(rect.width || rect.height),
                    }};
                }});
            }}""")

        def safe_click(page, selector=None, role=None, text=None):
            try:
                if selector:
                    locator = page.locator(selector).first
                elif role and text:
                    locator = page.get_by_role(role, name=text, exact=False).first
                else:
                    return False
                if locator.count() == 0:
                    return False
                locator.wait_for(state='visible', timeout=5000)
                locator.click(timeout=5000)
                page.wait_for_timeout(500)
                return True
            except Exception:
                return False

        def safe_select_option(page, selector, *, label=None, value=None):
            try:
                locator = page.locator(selector).first
                if locator.count() == 0:
                    return False
                locator.wait_for(state='visible', timeout=5000)
                if label is not None:
                    locator.select_option(label=label, timeout=5000)
                elif value is not None:
                    locator.select_option(value=value, timeout=5000)
                else:
                    return False
                page.wait_for_timeout(500)
                return True
            except Exception:
                return False

        def safe_fill(page, selector, value):
            try:
                locator = page.locator(selector).first
                if locator.count() == 0:
                    return False
                locator.wait_for(state='visible', timeout=5000)
                locator.fill(value, timeout=5000)
                page.wait_for_timeout(300)
                return True
            except Exception:
                return False

        def first_existing(page, selectors):
            for selector in selectors:
                try:
                    locator = page.locator(selector).first
                    if locator.count() > 0:
                        return selector
                except Exception:
                    continue
            return None

        summary = {repr(_build_generic_summary(url=url, vertical=vertical, project=project, backend="raw_playwright_probe", username=username, password=password))}

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(URL, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(1500)
            summary['current_url'] = page.url
            summary['elements_before_login'] = collect_elements(page)

            username_candidates = [
                "input[name='email']",
                "input[name='username']",
                "input[type='email']",
                "input[placeholder*='Email' i]",
                "input[placeholder*='Username' i]",
            ]
            password_candidates = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='Password' i]",
            ]
            submit_candidates = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Submit')",
                "button:has-text('Login')",
                "button:has-text('Sign in')",
            ]

            username_selector = first_existing(page, username_candidates)
            password_selector = first_existing(page, password_candidates)
            summary['username_selector'] = username_selector
            summary['password_selector'] = password_selector
            summary['submit_candidates'] = [selector for selector in submit_candidates if first_existing(page, [selector])]
            summary['login_detected'] = bool(username_selector and password_selector)

            if summary['login_detected']:
                summary['notes'].append('Login form detected on landing page.')
            else:
                summary['notes'].append('No explicit login form detected on landing page.')

            if USERNAME and PASSWORD and summary['login_detected']:
                summary['login_attempted'] = True
                filled_username = safe_fill(page, username_selector, USERNAME)
                filled_password = safe_fill(page, password_selector, PASSWORD)
                clicked = False
                for selector in submit_candidates:
                    if safe_click(page, selector=selector):
                        clicked = True
                        break
                if not clicked:
                    clicked = safe_click(page, role='button', text='Submit')
                page.wait_for_timeout(2500)
                summary['current_url'] = page.url
                summary['elements_after_login'] = collect_elements(page)
                summary['login_success_likely'] = bool(filled_username and filled_password and clicked and page.url != URL)
                if not clicked:
                    summary['notes'].append('Could not click a login submit control with the default candidate selectors.')
            else:
                summary['elements_after_login'] = summary['elements_before_login']

            select_selector = first_existing(page, ['mat-dialog-container select', 'mat-mdc-dialog-container select', 'select'])
            if select_selector:
                summary['notes'].append(f'Visible select detected for vertical flow: {{select_selector}}')
                vertical_selected = safe_select_option(page, select_selector, label=VERTICAL)
                if not vertical_selected:
                    vertical_selected = safe_select_option(page, select_selector, value=VERTICAL)
                if vertical_selected:
                    summary['notes'].append(f'Selected vertical using select_option on {{select_selector}}.')
                    safe_click(page, selector='mat-dialog-container button:has-text("Submit")') or safe_click(page, selector='mat-mdc-dialog-container button:has-text("Submit")') or safe_click(page, selector='button:has-text("Submit")')
                    page.wait_for_timeout(1500)
                    summary['elements_after_login'] = collect_elements(page)

            lower_vertical = VERTICAL.lower()
            lower_project = PROJECT.lower()
            summary['vertical_candidates'] = [
                el for el in summary['elements_after_login']
                if lower_vertical in ' '.join([
                    (el.get('text') or '').lower(),
                    (el.get('placeholder') or '').lower(),
                    (el.get('ariaLabel') or '').lower(),
                    (el.get('name') or '').lower(),
                ])
            ][:25]
            summary['project_candidates'] = [
                el for el in summary['elements_after_login']
                if lower_project in ' '.join([
                    (el.get('text') or '').lower(),
                    (el.get('placeholder') or '').lower(),
                    (el.get('ariaLabel') or '').lower(),
                    (el.get('name') or '').lower(),
                ])
            ][:25]
            browser.close()

        print(json.dumps(summary))
        '''
    )

    result = _run_python_script(script, timeout=60)
    output = result.get("stdout", "").strip()

    try:
        probe_inspection = json.loads(output) if output else {
            "notes": ["Inspection script produced no JSON output."]
        }
    except Exception as exc:
        probe_inspection = {
            "notes": [f"Inspection output could not be parsed: {exc}"],
            "raw_stdout": output[-4000:],
        }

    if result.get("stderr"):
        probe_inspection["stderr"] = result["stderr"][-4000:]
    if result.get("returncode"):
        probe_inspection["returncode"] = result["returncode"]

    for key, value in probe_inspection.items():
        if key == "notes":
            inspection.setdefault("notes", []).extend(value)
            continue
        if key in {"elements_before_login", "elements_after_login", "vertical_candidates", "project_candidates", "submit_candidates"}:
            if not inspection.get(key):
                inspection[key] = value
            continue
        if inspection.get(key) in (None, "", [], False):
            inspection[key] = value

    artifact_path = INSPECTION_DIR / f"inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    artifact_path.write_text(json.dumps(inspection, indent=2))
    inspection["artifact_path"] = str(artifact_path)
    return inspection
