from typing import TypedDict, Optional


class QAState(TypedDict):
    # ── Inputs ──────────────────────────────────────────────────────────
    ticket_id: str                   # e.g. "QA-42"
    app_url: str                     # URL of the app under test

    # ── Jira Ticket ──────────────────────────────────────────────────────
    ticket_summary: str
    ticket_description: str
    ticket_acceptance_criteria: str

    # ── Analysis ─────────────────────────────────────────────────────────
    risk_analysis: str               # GPT risk assessment
    risk_level: str                  # "LOW" | "MEDIUM" | "HIGH"

    # ── Test Generation ──────────────────────────────────────────────────
    test_cases: list[dict]           # list of structured test case dicts
    playwright_script: str           # generated Playwright Python script

    # ── Execution Results ────────────────────────────────────────────────
    test_results: list[dict]         # per-test pass/fail + details
    execution_error: Optional[str]   # raw execution error if any

    # ── Bug Detection ────────────────────────────────────────────────────
    bugs: list[dict]                 # classified bugs found
    is_selector_issue: bool          # True if self-heal retry needed

    # ── Jira Logging ─────────────────────────────────────────────────────
    jira_bug_links: list[str]        # URLs of created Jira bug tickets

    # ── Loop Control ─────────────────────────────────────────────────────
    retry_count: int                 # self-heal retry counter
    dom_snapshot: Optional[str]      # DOM context for self-healing

    # ── Final Output ─────────────────────────────────────────────────────
    summary: str                     # human-readable final report
