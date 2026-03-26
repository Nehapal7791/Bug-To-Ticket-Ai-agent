from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import QAState
from config import GROQ_MODEL
import json

llm = ChatGroq(model=GROQ_MODEL, temperature=0.3)


def gen_tests_node(state: QAState) -> QAState:
    """
    NODE 3: Generate structured test cases AND a Playwright script.
    On self-heal retries, uses DOM snapshot to fix selectors.
    """
    is_retry = state.get("retry_count", 0) > 0
    dom_context = ""
    if is_retry and state.get("dom_snapshot"):
        dom_context = f"""
⚠️ SELF-HEAL RETRY #{state['retry_count']}
The previous script had selector failures. Here is the live DOM snapshot:
{state['dom_snapshot']}

Use ONLY the selectors/IDs/test-IDs found in the DOM above.
"""

    risk_data = {}
    try:
        risk_data = json.loads(state.get("risk_analysis", "{}"))
    except Exception:
        pass

    prompt = f"""You are a QA automation engineer. Generate test cases and a Playwright script.

Ticket: {state['ticket_id']} — {state['ticket_summary']}
Description: {state['ticket_description']}
Acceptance Criteria: {state['ticket_acceptance_criteria']}
App URL: {state['app_url']}
Risk Level: {state.get('risk_level', 'MEDIUM')}
Key Areas: {risk_data.get('key_areas', [])}
Edge Cases: {risk_data.get('edge_cases', [])}
{dom_context}

Respond ONLY with a JSON object in exactly this format:
{{
  "test_cases": [
    {{
      "id": "TC001",
      "name": "descriptive test name",
      "category": "functional|ui|security|performance",
      "steps": ["step 1", "step 2"],
      "expected": "expected outcome",
      "priority": "HIGH|MEDIUM|LOW"
    }}
  ],
  "playwright_script": "FULL async Python playwright script here"
}}

PLAYWRIGHT SCRIPT RULES:
- Use `from playwright.sync_api import sync_playwright`
- Use sync API, not async
- Each test MUST call `_record("TC001 - test name", True/False, error=None)`
- Wrap each test in try/except — on exception call `_record("name", False, error=str(e))`
- Add `time.sleep(0.5)` between actions for stability
- Use `page.wait_for_selector()` before interacting with elements
- Target the app at: {state['app_url']}
- Import: import time, json, sys
- Do NOT include `if __name__ == "__main__"` block
- Do NOT redefine `_record` — it is injected automatically
"""

    response = llm.invoke([
        SystemMessage(content="You are a QA automation expert. Respond only with valid JSON."),
        HumanMessage(content=prompt),
    ])

    try:
        raw = response.content.strip().strip("```json").strip("```").strip()
        parsed = json.loads(raw)
        test_cases       = parsed.get("test_cases", [])
        playwright_script = parsed.get("playwright_script", "")
    except Exception as e:
        test_cases        = []
        playwright_script = f"# Generation failed: {e}\n_record('generation_error', False, error='{e}')\n"

    return {
        **state,
        "test_cases":        test_cases,
        "playwright_script": playwright_script,
    }
