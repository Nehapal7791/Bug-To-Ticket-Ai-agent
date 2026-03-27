import json

from graph.state import QAState
from tools.browser_inspector import inspect_application


def inspect_app_node(state: QAState) -> QAState:
    inspection = inspect_application(
        url=state["app_url"],
        username=state.get("username"),
        password=state.get("password"),
        vertical_name=state.get("vertical_name"),
        project_name=state.get("project_name"),
    )

    notes = inspection.get("notes", [])
    summary_parts = [
        f"login_detected={inspection.get('login_detected', False)}",
        f"login_attempted={inspection.get('login_attempted', False)}",
        f"login_success_likely={inspection.get('login_success_likely', False)}",
    ]

    if inspection.get("username_selector"):
        summary_parts.append(f"username_selector={inspection['username_selector']}")
    if inspection.get("password_selector"):
        summary_parts.append(f"password_selector={inspection['password_selector']}")
    if inspection.get("submit_candidates"):
        summary_parts.append(f"submit_candidates={inspection['submit_candidates']}")
    if inspection.get("vertical_candidates"):
        summary_parts.append(
            "vertical_candidates=" + json.dumps(inspection["vertical_candidates"][:5])
        )
    if inspection.get("project_candidates"):
        summary_parts.append(
            "project_candidates=" + json.dumps(inspection["project_candidates"][:5])
        )
    if notes:
        summary_parts.append("notes=" + " | ".join(notes[:5]))

    return {
        **state,
        "inspection_summary": "\n".join(summary_parts),
        "inspection_artifacts_path": inspection.get("artifact_path"),
        "dom_snapshot": state.get("dom_snapshot") or json.dumps(inspection.get("elements_after_login") or inspection.get("elements_before_login") or []),
    }
