"""
NODE 4: Execute tests using a ReAct agent with PlaywrightBrowserToolkit.

This replaces the old subprocess-based Playwright execution with an agentic approach
where the AI uses browser tools directly (navigate, click, extract) to execute test cases.
No Python code generation, no subprocess, no retry loop needed.
"""
import asyncio
import re
import json
from playwright.async_api import async_playwright
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import QAState
from config import GROQ_MODEL


def _build_test_prompt(test_case: dict, app_url: str, username: str | None, password: str | None) -> str:
    """Build the prompt for executing a single test case."""
    credentials_part = ""
    if username and password:
        credentials_part = f"""
Credentials available:
- Username: {username}
- Password: {password}

If the app requires login, navigate to the login page, find the username/email and password fields dynamically, fill them in, and submit the form. Wait for the authenticated state before proceeding with the test steps.
"""

    return f"""You are a QA automation engineer executing a test case on a web application.

Test Case ID: {test_case.get('id', 'TC001')}
Test Name: {test_case.get('name', 'Unnamed Test')}
App URL: {app_url}

Test Steps to execute:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(test_case.get('steps', [])))}

Expected Result: {test_case.get('expected', 'Test should pass')}
{credentials_part}

Instructions:
1. Navigate to the app URL first using the navigate_browser tool
2. Follow each test step carefully
3. Use the browser tools to interact: navigate_browser, click_element, extract_text, get_elements, current_page
4. If an element isn't found with one selector, try alternative approaches (different CSS selectors, text-based selectors, etc.)
5. After completing all steps, verify the expected result is met
6. Report the test result as passed or failed with details

Execute the test now."""


def _extract_test_result(agent_result: dict) -> dict:
    """Extract test result from agent output."""
    messages = agent_result.get("messages", [])
    if not messages:
        return {"passed": False, "error": "No response from agent"}

    # Get the last AI message content
    last_message = None
    for msg in reversed(messages):
        if hasattr(msg, 'content'):
            last_message = msg.content
            break
        elif isinstance(msg, tuple) and len(msg) >= 2:
            last_message = msg[1]
            break

    if not last_message:
        return {"passed": False, "error": "Could not extract agent response"}

    content = str(last_message).lower()

    # Determine pass/fail based on agent response content
    passed = any(word in content for word in ['pass', 'success', 'completed', 'expected result met', 'verification successful'])
    failed = any(word in content for word in ['fail', 'error', 'could not', 'unable to', 'not found', 'timeout'])

    if passed and not failed:
        return {"passed": True, "details": str(last_message)[:500]}
    elif failed:
        return {"passed": False, "error": str(last_message)[:500]}
    else:
        # Ambiguous - treat as passed if no clear failure indicators
        return {"passed": True, "details": str(last_message)[:500]}


async def execute_playwright_action(page, action: str, args: dict) -> str:
    """Execute a single Playwright action on the page."""
    try:
        if action == "navigate_browser":
            url = args.get("url", "")
            await page.goto(url)
            return f"Navigated to {url}"
        
        elif action == "click_element":
            selector = args.get("selector", "")
            await page.click(selector, timeout=5000)
            return f"Clicked {selector}"
        
        elif action == "extract_text":
            selector = args.get("selector", "body")
            text = await page.text_content(selector)
            return text or ""
        
        elif action == "get_elements":
            selector = args.get("selector", "")
            elements = await page.query_selector_all(selector)
            return f"Found {len(elements)} elements matching {selector}"
        
        elif action == "current_page":
            return page.url
        
        else:
            return f"Unknown action: {action}"
    
    except Exception as e:
        return f"Error executing {action}: {str(e)[:100]}"


async def run_single_test_async(test_case: dict, app_url: str, username: str | None, password: str | None) -> dict:
    """
    Execute a single test case with its own browser instance.
    Since Groq doesn't support native tool calling, we parse text output and execute tools manually.
    """
    test_id = test_case.get("id", "unknown")
    test_name = test_case.get("name", "Unnamed Test")
    
    playwright = None
    browser = None
    page = None
    
    try:
        # Start Playwright and launch browser (visible)
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Initialize LLM
        llm = ChatGroq(model=GROQ_MODEL, temperature=0)

        # Build prompt for this test case
        test_prompt = _build_test_prompt(test_case, app_url, username, password)
        
        # System prompt to guide the LLM to output executable actions
        system_prompt = """You are a QA test automation assistant. Execute the test by outputting ONE action at a time in this format:
ACTION: action_name
ARGS: {"key": "value"}

Available actions:
- navigate_browser: {"url": "https://example.com"}
- click_element: {"selector": "button#login"}
- extract_text: {"selector": "div.message"}
- get_elements: {"selector": ".item"}

After each action, I will tell you the result. Then output the next action.
When test is complete, output: COMPLETE: PASS or COMPLETE: FAIL with reason."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=test_prompt)
        ]
        
        execution_log = []
        max_iterations = 20
        
        for iteration in range(max_iterations):
            # Get LLM response
            response = await llm.ainvoke(messages)
            response_text = response.content
            
            execution_log.append(f"LLM: {response_text[:200]}")
            
            # Check if test is complete
            if "COMPLETE:" in response_text:
                passed = "PASS" in response_text
                return {
                    "test_id": test_id,
                    "test_name": test_name,
                    "passed": passed,
                    "details" if passed else "error": "\n".join(execution_log),
                    "steps": test_case.get("steps", []),
                    "expected": test_case.get("expected", "")
                }
            
            # Parse action from response
            action_match = re.search(r'ACTION:\s*(\w+)', response_text)
            args_match = re.search(r'ARGS:\s*({[^}]+})', response_text)
            
            if action_match and args_match:
                action = action_match.group(1)
                try:
                    args = json.loads(args_match.group(1))
                except (json.JSONDecodeError, ValueError):
                    args = {}
                
                # Execute the action
                result = await execute_playwright_action(page, action, args)
                execution_log.append(f"Executed {action}: {result[:100]}")
                
                # Add result to conversation
                messages.append(response)
                messages.append(HumanMessage(content=f"Result: {result}\nWhat's the next action?"))
            else:
                # LLM didn't follow format, try to continue
                messages.append(response)
                messages.append(HumanMessage(content="Please output the next action in the correct format: ACTION: ... ARGS: ..."))
        
        # Max iterations reached
        return {
            "test_id": test_id,
            "test_name": test_name,
            "passed": False,
            "error": f"Test exceeded max iterations. Log: {' | '.join(execution_log[-5:])}",
            "steps": test_case.get("steps", []),
            "expected": test_case.get("expected", "")
        }

    except Exception as e:
        return {
            "test_id": test_id,
            "test_name": test_name,
            "passed": False,
            "error": str(e)[:500],
        }

    finally:
        # Clean up browser and playwright
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        if playwright:
            try:
                await playwright.stop()
            except Exception:
                pass


def run_playwright_agent(state: QAState) -> QAState:
    """
    Execute test cases using a ReAct agent with browser tools.
    Each test case gets its own browser instance to avoid conflicts.
    Runs in async context compatible with LangGraph.
    """
    test_cases = state.get("test_cases", [])
    app_url = state.get("app_url", "")
    username = state.get("username")
    password = state.get("password")

    if not test_cases:
        return {
            **state,
            "test_results": [{"passed": False, "error": "No test cases to execute"}],
            "execution_error": "No test cases provided",
        }

    # Run all tests sequentially (each with its own browser)
    async def run_all_tests():
        results = []
        errors = []
        
        for test_case in test_cases:
            result = await run_single_test_async(test_case, app_url, username, password)
            results.append(result)
            
            if not result.get("passed") and result.get("error"):
                test_id = result.get("test_id", "unknown")
                errors.append(f"{test_id}: {result['error'][:200]}")
        
        return results, errors
    
    # Execute async tests (creates new event loop if needed)
    try:
        # Try to get running loop first
        loop = asyncio.get_running_loop()
        # If we're already in an async context, this shouldn't happen in LangGraph nodes
        import nest_asyncio
        nest_asyncio.apply()
        test_results, execution_errors = loop.run_until_complete(run_all_tests())
    except RuntimeError:
        # No running loop - create one with asyncio.run()
        test_results, execution_errors = asyncio.run(run_all_tests())

    return {
        **state,
        "test_results": test_results,
        "execution_error": "; ".join(execution_errors) if execution_errors else None,
    }


def run_playwright_node(state: QAState) -> QAState:
    """
    Execute Playwright tests using ReAct agent.
    Now fully synchronous to work seamlessly with LangGraph.
    """
    return run_playwright_agent(state)
