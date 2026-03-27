from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import QAState
from config import GROQ_MODEL
import json

llm = None


def get_llm():
    global llm
    if llm is None:
        llm = ChatGroq(model=GROQ_MODEL, temperature=0.1)
    return llm


def detect_bugs_node(state: QAState) -> QAState:
    """
    NODE 5: Classify test failures.
    - Real bugs → log to Jira
    - All infrastructure issues are now handled by the ReAct agent internally
    """
    test_results  = state.get("test_results", [])
    failed_tests  = [t for t in test_results if not t.get("passed")]

    if not failed_tests:
        return {**state, "bugs": []}

    prompt = f"""You are a QA bug analyst. Classify these test failures.

Ticket: {state['ticket_id']} — {state['ticket_summary']}
App URL: {state['app_url']}

Failed Tests:
{json.dumps(failed_tests, indent=2)}

For each failure, determine:
1. Is this a REAL APPLICATION BUG or a TEST INFRASTRUCTURE issue?
   - Real bugs: wrong behavior, wrong content, HTTP errors, logic failures
   - Infrastructure: element not found, selector timeout, network timeout, wrong URL
   
Note: Infrastructure issues are now handled internally by the ReAct agent, 
so only classify as INFRASTRUCTURE if it's clearly not an application bug.
Real bugs should be logged to Jira.

Respond ONLY with JSON:
{{
  "bugs": [
    {{
      "test_id": "TC001",
      "test_name": "test name",
      "bug_type": "REAL_BUG" | "INFRASTRUCTURE",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "title": "short bug title",
      "description": "detailed description with steps to reproduce",
      "expected": "expected behavior",
      "actual": "actual behavior"
    }}
  ],
  "has_real_bugs": true | false
}}"""

    response = get_llm().invoke([
        SystemMessage(content="You are a QA bug classifier. Respond only with valid JSON."),
        HumanMessage(content=prompt),
    ])

    try:
        raw = response.content.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)
    except Exception:
        data = {
            "bugs": [],
            "has_real_bugs": False,
        }

    real_bugs = [b for b in data.get("bugs", []) if b.get("bug_type") == "REAL_BUG"]

    return {
        **state,
        "bugs": real_bugs,
    }
