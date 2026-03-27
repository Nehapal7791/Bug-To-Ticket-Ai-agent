from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import QAState
from config import GROQ_MODEL, APP_VERTICAL_NAME, APP_PROJECT_NAME
import json
import ast
import re
from pydantic import BaseModel, ValidationError


class TestCaseModel(BaseModel):
    id: str
    name: str
    category: str
    steps: list[str]
    expected: str
    priority: str


class GeneratedTestsModel(BaseModel):
    test_cases: list[TestCaseModel]
    # playwright_script removed - now using ReAct agent with browser tools

llm = None


def get_llm():
    global llm
    if llm is None:
        llm = ChatGroq(model=GROQ_MODEL, temperature=0.3)
    return llm


def _extract_json_block(raw_text: str) -> str:
    cleaned = raw_text.strip()
    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start:end + 1].strip()
    return cleaned


def _extract_string_field(block: str, field_name: str) -> str | None:
    marker = f'"{field_name}"'
    key_index = block.find(marker)
    if key_index == -1:
        return None

    colon_index = block.find(":", key_index + len(marker))
    if colon_index == -1:
        return None

    first_quote = block.find('"', colon_index + 1)
    if first_quote == -1:
        return None

    cursor = first_quote + 1
    escaped = False
    collected: list[str] = []
    while cursor < len(block):
        char = block[cursor]
        if escaped:
            if char == "n":
                collected.append("\n")
            elif char == "t":
                collected.append("\t")
            elif char == '"':
                collected.append('"')
            elif char == "\\":
                collected.append("\\")
            else:
                collected.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return "".join(collected)
        else:
            collected.append(char)
        cursor += 1
    return None


def _parse_generated_tests(raw_text: str) -> GeneratedTestsModel:
    json_block = _extract_json_block(raw_text)
    parse_errors: list[str] = []

    try:
        return GeneratedTestsModel.model_validate_json(json_block)
    except (ValidationError, json.JSONDecodeError) as exc:
        parse_errors.append(f"model_validate_json failed: {exc}")

    try:
        parsed = json.loads(json_block)
        return GeneratedTestsModel.model_validate(parsed)
    except (ValidationError, json.JSONDecodeError) as exc:
        parse_errors.append(f"json.loads failed: {exc}")

    try:
        parsed = ast.literal_eval(json_block)
        return GeneratedTestsModel.model_validate(parsed)
    except (ValidationError, SyntaxError, ValueError) as exc:
        parse_errors.append(f"ast.literal_eval failed: {exc}")

    test_cases_match = re.search(r'"test_cases"\s*:\s*(\[.*?\])\s*}', json_block, re.DOTALL)
    if test_cases_match:
        try:
            test_cases = json.loads(test_cases_match.group(1))
            return GeneratedTestsModel.model_validate(
                {
                    "test_cases": test_cases,
                }
            )
        except (ValidationError, json.JSONDecodeError) as exc:
            parse_errors.append(f"test_cases extraction failed: {exc}")

    raise ValueError("; ".join(parse_errors))


def gen_tests_node(state: QAState) -> QAState:
    """
    NODE 3: Generate structured test cases.
    
    Note: Playwright script generation is removed. Tests are now executed
    by a ReAct agent with browser tools (see run_playwright.py).
    The agent dynamically handles navigation, clicks, and assertions.
    """
    is_retry = state.get("retry_count", 0) > 0
    dom_context = ""
    if is_retry:
        dom_context = f"""
⚠️ RETRY ATTEMPT #{state['retry_count']}
Previous test execution had issues. Review and improve test case clarity.
"""

    inspection_context = ""
    if state.get("inspection_summary"):
        inspection_context = f"""
LIVE APP INSPECTION RESULTS:
{state['inspection_summary']}

Use the selectors and candidate elements from this inspection as the primary grounding source.
If the inspection discovered login or selection candidates, prefer those over guessed selectors.
Inspection artifact: {state.get('inspection_artifacts_path')}
"""

    risk_data = {}
    try:
        risk_data = json.loads(state.get("risk_analysis", "{}"))
    except Exception:
        pass

    required_vertical = state.get("vertical_name") or APP_VERTICAL_NAME
    required_project = state.get("project_name") or APP_PROJECT_NAME

    login_context = f"""
Login Credentials Provided:
- Username: {state['username']}
- Password: {state['password']}

LOGIN GUIDANCE:
- Include test steps for login where relevant (e.g., "Navigate to login page", "Enter username", "Enter password", "Click login button")
- The AI agent will dynamically locate login fields - you don't need selectors
- Include tests that verify successful login flow
"""

    project_context = f"""
PROJECT-SPECIFIC GUIDANCE:
- For this application, vertical is `{required_vertical}` and project is `{required_project}`.
- Include test steps for selecting these if relevant to the ticket.
- The AI agent will dynamically find selection controls.
"""

    prompt = f"""You are a QA automation engineer. Generate structured test cases for validation.

Ticket: {state['ticket_id']} — {state['ticket_summary']}
Description: {state['ticket_description']}
Acceptance Criteria: {state['ticket_acceptance_criteria']}
App URL: {state['app_url']}
Risk Level: {state.get('risk_level', 'MEDIUM')}
Key Areas: {risk_data.get('key_areas', [])}
Edge Cases: {risk_data.get('edge_cases', [])}
{dom_context}
{project_context}
{login_context}
{inspection_context}

IMPORTANT: Test cases will be executed by an AI agent with browser automation tools (navigate, click, extract_text, get_elements). The agent will handle all interactions dynamically - you only need to describe WHAT to test, not HOW to click/select.

Respond ONLY with a JSON object in exactly this format:
{{
  "test_cases": [
    {{
      "id": "TC001",
      "name": "descriptive test name",
      "category": "functional|ui|security|performance",
      "steps": ["step 1 - describe the action", "step 2 - describe the action"],
      "expected": "expected outcome",
      "priority": "HIGH|MEDIUM|LOW"
    }}
  ]
}}

TEST CASE RULES:
- Generate 3-6 test cases covering the ticket requirements
- Steps should be descriptive actions an AI can understand (e.g., "Navigate to login page", "Fill username field", "Click submit button")
- The AI agent will dynamically find selectors - do NOT include CSS selectors or XPath in steps
- If credentials are provided, include steps for login in relevant test cases
- Include tests for both happy path and edge cases
- Do NOT generate Playwright Python code - the agent handles execution
- Focus on user intent and expected outcomes
"""

    response = get_llm().invoke([
        SystemMessage(content="You are a QA automation expert. Respond only with valid JSON."),
        HumanMessage(content=prompt),
    ])

    raw_response = response.content.strip()

    try:
        generated = _parse_generated_tests(raw_response)
        test_cases = [test_case.model_dump() for test_case in generated.test_cases]
        if not test_cases:
            raise ValueError("LLM returned empty test cases")
    except Exception:
        test_cases = []

    return {
        **state,
        "test_cases": test_cases,
        "playwright_script": "# ReAct agent mode - no script generation needed",
        "generation_raw_output": raw_response,
    }
