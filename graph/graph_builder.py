from langgraph.graph import StateGraph, END
from graph.state import QAState
from graph.nodes.fetch_ticket   import fetch_ticket_node
from graph.nodes.analyze_risk   import analyze_risk_node
from graph.nodes.gen_tests      import gen_tests_node
from graph.nodes.run_playwright import run_playwright_node
from graph.nodes.detect_bugs    import detect_bugs_node
from graph.nodes.self_heal      import self_heal_node
from graph.nodes.log_bugs       import log_bugs_node
from graph.nodes.summarize      import summarize_node
from config import MAX_SELF_HEAL_RETRIES


# ── Conditional edge functions ────────────────────────────────────────────────

def route_after_detect(state: QAState) -> str:
    """
    After bug detection, route to one of:
    - "self_heal"  → selector issues, retry limit not hit
    - "log_bugs"   → real bugs found
    - "summarize"  → all passed, nothing to log
    """
    if state.get("is_selector_issue") and state.get("retry_count", 0) < MAX_SELF_HEAL_RETRIES:
        return "self_heal"
    if state.get("bugs"):
        return "log_bugs"
    return "summarize"


def route_after_self_heal(state: QAState) -> str:
    """Self-heal always loops back to regenerate tests."""
    return "gen_tests"


# ── Build the graph ───────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(QAState)

    # ── Register nodes ───────────────────────────────────────────────────────
    graph.add_node("fetch_ticket",    fetch_ticket_node)
    graph.add_node("analyze_risk",    analyze_risk_node)
    graph.add_node("gen_tests",       gen_tests_node)
    graph.add_node("run_playwright",  run_playwright_node)
    graph.add_node("detect_bugs",     detect_bugs_node)
    graph.add_node("self_heal",       self_heal_node)
    graph.add_node("log_bugs",        log_bugs_node)
    graph.add_node("summarize",       summarize_node)

    # ── Entry point ──────────────────────────────────────────────────────────
    graph.set_entry_point("fetch_ticket")

    # ── Linear edges ─────────────────────────────────────────────────────────
    graph.add_edge("fetch_ticket",   "analyze_risk")
    graph.add_edge("analyze_risk",   "gen_tests")
    graph.add_edge("gen_tests",      "run_playwright")
    graph.add_edge("run_playwright", "detect_bugs")

    # ── Conditional edge: after detect_bugs ──────────────────────────────────
    graph.add_conditional_edges(
        "detect_bugs",
        route_after_detect,
        {
            "self_heal": "self_heal",
            "log_bugs":  "log_bugs",
            "summarize": "summarize",
        }
    )

    # ── Agentic loop: self_heal → gen_tests (retry) ──────────────────────────
    graph.add_conditional_edges(
        "self_heal",
        route_after_self_heal,
        {"gen_tests": "gen_tests"}
    )

    # ── Terminal edges ───────────────────────────────────────────────────────
    graph.add_edge("log_bugs",  "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()
