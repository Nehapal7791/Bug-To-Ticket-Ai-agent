from graph.state import QAState
from tools.jira_client import fetch_ticket as jira_fetch
from config import APP_BASE_URL


def fetch_ticket_node(state: QAState) -> QAState:
    """
    NODE 1: Fetch Jira ticket data and load into state.
    """
    ticket_id = state["ticket_id"]
    data = jira_fetch(ticket_id)

    return {
        **state,
        "ticket_summary":            data["summary"],
        "ticket_description":        data["description"],
        "ticket_acceptance_criteria": data["acceptance_criteria"],
        "app_url":                   state.get("app_url") or APP_BASE_URL,
        "retry_count":               0,
        "bugs":                      [],
        "jira_bug_links":            [],
        "is_selector_issue":         False,
    }
