from typing import TypedDict, Optional


class QAState(TypedDict):
    # ── Inputs ──────────────────────────────────────────────────────────
    ticket_id: str                   # e.g. "QA-42"
    app_url: str                     # URL of the app under test
    username: Optional[str]          # login username/email for app auth
    password: Optional[str]          # login password for app auth
    vertical_name: Optional[str]     # vertical to select after login
    project_name: Optional[str]      # project to select after login
    inspection_summary: Optional[str]
    inspection_artifacts_path: Optional[str]

    # ── Jira Ticket ──────────────────────────────────────────────────────
    ticket_summary: str
    ticket_description: str
    ticket_acceptance_criteria: str

    # ── Analysis ─────────────────────────────────────────────────────────
    risk_analysis: str               # GPT risk assessment
    risk_level: str                  # "LOW" | "MEDIUM" | "HIGH"

    # ── Test Generation ──────────────────────────────────────────────────
    test_cases: list[dict]           # list of structured test case dicts
    playwright_script: str           # kept for compatibility (now agent mode)

    # ── Execution Results ────────────────────────────────────────────────
    test_results: list[dict]         # per-test pass/fail + details
    execution_error: Optional[str]   # raw execution error if any
    generated_script_path: Optional[str]
    executed_script_path: Optional[str]
    execution_stdout: Optional[str]
    execution_stderr: Optional[str]

    # ── Bug Detection ────────────────────────────────────────────────────
    bugs: list[dict]                 # classified bugs found

    # ── Jira Logging ─────────────────────────────────────────────────────
    jira_bug_links: list[str]        # URLs of created Jira bug tickets

    # ── Final Output ─────────────────────────────────────────────────────
    summary: str                     # human-readable final report
