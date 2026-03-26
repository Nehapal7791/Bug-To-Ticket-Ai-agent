from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import QAState
from config import GROQ_MODEL
import json

llm = ChatGroq(model=GROQ_MODEL, temperature=0.4)


def summarize_node(state: QAState) -> QAState:
    """
    NODE 8 (terminal): Generate a clean final QA report summary.
    """
    test_results = state.get("test_results", [])
    total   = len(test_results)
    passed  = sum(1 for t in test_results if t.get("passed"))
    failed  = total - passed
    bugs    = state.get("bugs", [])
    links   = state.get("jira_bug_links", [])

    prompt = f"""You are a QA lead writing an executive test summary.

Ticket: {state['ticket_id']} — {state['ticket_summary']}
Risk Level: {state.get('risk_level', 'UNKNOWN')}
Total Tests: {total} | Passed: {passed} | Failed: {failed}
Real Bugs Found: {len(bugs)}
Jira Bug Tickets Created: {len(links)}
Self-Heal Retries Used: {state.get('retry_count', 0)}

Bugs:
{json.dumps(bugs, indent=2) if bugs else 'None'}

Write a clear 3-paragraph executive summary:
1. Overall QA result and confidence level
2. Key issues found (or confirmation of quality)
3. Recommendation (deploy / fix first / needs manual review)

Be concise and professional."""

    response = llm.invoke([
        SystemMessage(content="You are a QA lead writing executive reports."),
        HumanMessage(content=prompt),
    ])

    return {
        **state,
        "summary": response.content.strip(),
    }
