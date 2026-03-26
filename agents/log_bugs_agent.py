from graph.state import QAState
from tools.jira_client import create_bug_ticket


def log_bugs_node(state: QAState) -> QAState:
    """
    NODE 7: Create Jira bug tickets for every real bug detected.
    """
    bugs  = state.get("bugs", [])
    links = []

    for bug in bugs:
        description = f"""
*Test Case:* {bug.get('test_id')} — {bug.get('test_name')}

*Expected Behavior:*
{bug.get('expected', 'N/A')}

*Actual Behavior:*
{bug.get('actual', 'N/A')}

*Full Details:*
{bug.get('description', '')}
"""
        try:
            url = create_bug_ticket(
                summary=bug.get("title", "Untitled Bug"),
                description=description,
                related_ticket_id=state["ticket_id"],
                severity=bug.get("severity", "MEDIUM"),
            )
            links.append(url)
        except Exception as e:
            links.append(f"FAILED_TO_CREATE: {e}")

    return {
        **state,
        "jira_bug_links": links,
    }
