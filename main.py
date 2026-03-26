"""
╔══════════════════════════════════════════════════════════╗
║          AI-POWERED QA AGENT  —  LangGraph + GPT         ║
║      Test Gen · Playwright Execution · Jira Logging      ║
╚══════════════════════════════════════════════════════════╝

Usage:
    python main.py --ticket QA-42
    python main.py --ticket QA-42 --app https://myapp.com
"""

import argparse
import json
import sys
import time
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich import box

from graph.graph_builder import build_graph
from config import APP_BASE_URL

console = Console()

NODE_LABELS = {
    "fetch_ticket":   "📋  Fetching Jira ticket",
    "analyze_risk":   "🔍  Analyzing risk",
    "gen_tests":      "✍️   Generating test cases",
    "run_playwright": "🎭  Running Playwright tests",
    "detect_bugs":    "🐛  Detecting bugs",
    "self_heal":      "🔧  Self-healing selectors",
    "log_bugs":       "📝  Logging bugs to Jira",
    "summarize":      "📊  Generating report",
}


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]AI QA AGENT[/bold cyan]  [dim]powered by LangGraph + Groq (llama3)[/dim]\n"
        "[dim]Test Generation · Playwright · Self-Healing · Jira Integration[/dim]",
        border_style="cyan"
    ))


def print_state_update(node_name: str, state: dict):
    label = NODE_LABELS.get(node_name, f"⚙️  {node_name}")
    console.print(f"  [green]✓[/green] {label}")

    # Print node-specific highlights
    if node_name == "fetch_ticket":
        console.print(f"    [dim]→ {state.get('ticket_summary', '')[:80]}[/dim]")

    elif node_name == "analyze_risk":
        level = state.get("risk_level", "?")
        color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(level, "white")
        console.print(f"    [dim]→ Risk Level: [{color}]{level}[/{color}][/dim]")

    elif node_name == "gen_tests":
        count = len(state.get("test_cases", []))
        retry = state.get("retry_count", 0)
        tag   = f" [yellow](retry #{retry})[/yellow]" if retry > 0 else ""
        console.print(f"    [dim]→ Generated {count} test cases{tag}[/dim]")

    elif node_name == "run_playwright":
        results = state.get("test_results", [])
        total  = len(results)
        passed = sum(1 for r in results if r.get("passed"))
        failed = total - passed
        console.print(f"    [dim]→ {total} tests: [green]{passed} passed[/green] / [red]{failed} failed[/red][/dim]")

    elif node_name == "self_heal":
        console.print(f"    [yellow]→ Selector issues detected — regenerating with DOM context...[/yellow]")

    elif node_name == "detect_bugs":
        bugs = state.get("bugs", [])
        if bugs:
            console.print(f"    [dim]→ [red]{len(bugs)} real bug(s) found[/red][/dim]")
        else:
            console.print(f"    [dim]→ [green]No real bugs detected[/green][/dim]")

    elif node_name == "log_bugs":
        links = state.get("jira_bug_links", [])
        for link in links:
            console.print(f"    [dim]→ [blue]{link}[/blue][/dim]")


def print_test_table(state: dict):
    results = state.get("test_results", [])
    if not results:
        return

    table = Table(title="Test Results", box=box.ROUNDED, border_style="dim")
    table.add_column("ID",       style="dim",   width=8)
    table.add_column("Test Name", style="white", width=45)
    table.add_column("Status",   width=10)
    table.add_column("Details",  style="dim",   width=40)

    test_cases = state.get("test_cases", [])
    tc_map = {tc.get("id", ""): tc for tc in test_cases}

    for r in results:
        name    = r.get("name", "Unknown")
        passed  = r.get("passed", False)
        error   = r.get("error") or r.get("details") or ""
        tc_id   = name.split(" - ")[0] if " - " in name else "—"
        tc_info = tc_map.get(tc_id, {})
        status  = "[green]✅ PASS[/green]" if passed else "[red]❌ FAIL[/red]"

        table.add_row(tc_id, name[:44], status, error[:39])

    console.print()
    console.print(table)


def print_final_report(state: dict):
    bugs  = state.get("bugs", [])
    links = state.get("jira_bug_links", [])

    console.print()
    console.print(Panel(
        state.get("summary", "No summary generated."),
        title="[bold]Executive QA Summary[/bold]",
        border_style="cyan",
        padding=(1, 2),
    ))

    if bugs:
        console.print()
        bug_table = Table(title="Bugs Logged to Jira", box=box.SIMPLE_HEAD, border_style="red")
        bug_table.add_column("Severity", width=10)
        bug_table.add_column("Title",    width=50)
        bug_table.add_column("Jira Link", width=50)

        for bug, link in zip(bugs, links):
            sev   = bug.get("severity", "?")
            color = {"CRITICAL": "red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(sev, "white")
            bug_table.add_row(
                f"[{color}]{sev}[/{color}]",
                bug.get("title", "")[:49],
                f"[blue]{link}[/blue]",
            )
        console.print(bug_table)

    # Stats panel
    results = state.get("test_results", [])
    total   = len(results)
    passed  = sum(1 for r in results if r.get("passed"))

    console.print()
    console.print(
        f"  [bold]Ticket:[/bold] {state.get('ticket_id')}  "
        f"[bold]Tests:[/bold] {total}  "
        f"[bold]Passed:[/bold] [green]{passed}[/green]  "
        f"[bold]Bugs:[/bold] [red]{len(bugs)}[/red]  "
        f"[bold]Retries:[/bold] {state.get('retry_count', 0)}"
    )


def run_agent(ticket_id: str, app_url: str):
    print_banner()
    console.print(f"\n[bold]Running QA Agent[/bold] for ticket [cyan]{ticket_id}[/cyan]\n")

    graph = build_graph()

    initial_state: dict = {
        "ticket_id":                  ticket_id,
        "app_url":                    app_url,
        "ticket_summary":             "",
        "ticket_description":         "",
        "ticket_acceptance_criteria": "",
        "risk_analysis":              "",
        "risk_level":                 "",
        "test_cases":                 [],
        "playwright_script":          "",
        "test_results":               [],
        "execution_error":            None,
        "bugs":                       [],
        "is_selector_issue":          False,
        "jira_bug_links":             [],
        "retry_count":                0,
        "dom_snapshot":               None,
        "summary":                    "",
    }

    console.print("[dim]Starting LangGraph agentic loop...[/dim]\n")
    final_state = initial_state

    for step in graph.stream(initial_state):
        for node_name, state in step.items():
            final_state = state
            print_state_update(node_name, state)

    print_test_table(final_state)
    print_final_report(final_state)

    # Save full report
    report_path = f"reports/{ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        # Remove non-serializable fields
        safe_state = {k: v for k, v in final_state.items() if isinstance(v, (str, int, bool, list, dict, type(None)))}
        json.dump(safe_state, f, indent=2)

    console.print(f"\n  [dim]Full report saved → {report_path}[/dim]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI QA Agent — LangGraph + GPT-4o-mini")
    parser.add_argument("--ticket", required=True, help="Jira ticket ID, e.g. QA-42")
    parser.add_argument("--app",    default=APP_BASE_URL, help="App URL to test against")
    args = parser.parse_args()

    try:
        run_agent(args.ticket, args.app)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error:[/red] {e}")
        raise