from jira import JIRA
from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY


def get_jira_client() -> JIRA:
    return JIRA(
        server=JIRA_BASE_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )


def fetch_ticket(ticket_id: str) -> dict:
    """Fetch a Jira ticket and return its key fields."""
    jira = get_jira_client()
    issue = jira.issue(ticket_id)
    fields = issue.fields

    # Extract acceptance criteria from description or custom field
    description = fields.description or ""
    acceptance_criteria = ""
    if "acceptance criteria" in description.lower():
        parts = description.lower().split("acceptance criteria")
        if len(parts) > 1:
            acceptance_criteria = parts[1].strip()

    return {
        "id": ticket_id,
        "summary": fields.summary or "",
        "description": description,
        "acceptance_criteria": acceptance_criteria,
        "issue_type": str(fields.issuetype),
        "status": str(fields.status),
        "priority": str(fields.priority) if fields.priority else "Medium",
    }


def create_bug_ticket(
    summary: str,
    description: str,
    related_ticket_id: str,
    severity: str = "Medium",
) -> str:
    """Create a bug ticket in Jira and return its URL."""
    jira = get_jira_client()

    priority_map = {
        "CRITICAL": "Highest",
        "HIGH": "High",
        "MEDIUM": "Medium",
        "LOW": "Low",
    }

    issue_dict = {
        "project": {"key": JIRA_PROJECT_KEY},
        "summary": f"[AI-QA] {summary}",
        "description": (
            f"*Auto-detected by AI QA Agent*\n\n"
            f"*Related Ticket:* {related_ticket_id}\n\n"
            f"*Severity:* {severity}\n\n"
            f"----\n\n{description}"
        ),
        "issuetype": {"name": "Bug"},
        "priority": {"name": priority_map.get(severity.upper(), "Medium")},
    }

    new_issue = jira.create_issue(fields=issue_dict)
    return f"{JIRA_BASE_URL}/browse/{new_issue.key}"
