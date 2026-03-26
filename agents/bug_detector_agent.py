from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import QAState
from config import GROQ_MODEL
import json

llm = ChatGroq(model=GROQ_MODEL, temperature=0.1)


def detect_bugs_node(state: QAState) -> QAState:
    """
    NODE 5: Classify test failures.
    - Real bugs → log to Jira
    - Selector/infra issues → trigger self-heal retry
    """
    test_results  = state.get("test_results", [])
    failed_tests  = [t for t in test_results if not t.get("passed")]

    if not failed_tests:
        return {**state, "bugs": [], "is_selector_issue": False}

    prompt = f"""You are a QA bug analyst. Classify these test failures.

Ticket: {state['ticket_id']} — {state['ticket_summary']}
App URL: {state['app_url']}

Failed Tests:
{json.dumps(failed_tests, indent=2)}

For each failure, determine:
1. Is this a REAL APPLICATION BUG or a TEST INFRASTRUCTURE issue?
   - Real bugs: wrong behavior, wrong content, HTTP errors, logic failures
   - Infrastructure: element not found, selector timeout, network timeout, wrong URL

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
      "actual": "actual behavior",
      "selector_issue": false
    }}
  ],
  "has_selector_issues": true | false,
  "has_real_bugs": true | false
}}"""

    response = llm.invoke([
        SystemMessage(content="You are a QA bug classifier. Respond only with valid JSON."),
        HumanMessage(content=prompt),
    ])

    try:
        raw = response.content.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)
    except Exception:
        data = {
            "bugs": [],
            "has_selector_issues": True,
            "has_real_bugs": False,
        }

    real_bugs        = [b for b in data.get("bugs", []) if b.get("bug_type") == "REAL_BUG"]
    has_sel_issues   = data.get("has_selector_issues", False)
    retry_count      = state.get("retry_count", 0)
    from config import MAX_SELF_HEAL_RETRIES
    should_self_heal = has_sel_issues and not data.get("has_real_bugs") and retry_count < MAX_SELF_HEAL_RETRIES

    return {
        **state,
        "bugs":             real_bugs,
        "is_selector_issue": should_self_heal,
    }
