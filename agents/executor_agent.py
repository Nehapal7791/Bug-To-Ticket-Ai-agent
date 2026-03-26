from graph.state import QAState
from tools.playwright_runner import run_playwright_script, capture_dom_snapshot
from pathlib import Path


def run_playwright_node(state: QAState) -> QAState:
    """
    NODE 4: Execute the generated Playwright script.
    Also saves the script to tests/generated/ for audit trail.
    """
    script = state.get("playwright_script", "")

    # Save generated script for audit
    script_path = Path(f"tests/generated/{state['ticket_id']}_test.py")
    script_path.parent.mkdir(exist_ok=True)
    script_path.write_text(script)

    # Execute
    results = run_playwright_script(script)

    # If execution errored hard, grab DOM snapshot for self-heal
    dom_snapshot = state.get("dom_snapshot", "")
    if results.get("status") in ("FAIL", "EXECUTION_ERROR") and not dom_snapshot:
        dom_snapshot = capture_dom_snapshot(state["app_url"])

    return {
        **state,
        "test_results":   results.get("tests", []),
        "execution_error": results.get("error"),
        "dom_snapshot":   dom_snapshot,
    }
