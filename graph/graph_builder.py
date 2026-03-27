from langgraph.graph import StateGraph, END
from graph.state import QAState
from graph.nodes.fetch_ticket   import fetch_ticket_node
from graph.nodes.analyze_risk   import analyze_risk_node
from graph.nodes.inspect_app    import inspect_app_node
from graph.nodes.gen_tests      import gen_tests_node
from graph.nodes.run_playwright import run_playwright_node
from graph.nodes.detect_bugs    import detect_bugs_node
from graph.nodes.log_bugs       import log_bugs_node
from graph.nodes.summarize      import summarize_node


# ── Conditional edge functions ────────────────────────────────────────────────

def route_after_detect(state: QAState) -> str:
    """
    After bug detection, route to:
    - "log_bugs"   → bugs found
    - "summarize"  → all passed, nothing to log
    """
    if state.get("bugs"):
        return "log_bugs"
    return "summarize"



# ── Build the graph ───────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(QAState)

    # ── Register nodes ───────────────────────────────────────────────────────
    graph.add_node("fetch_ticket",    fetch_ticket_node)
    graph.add_node("analyze_risk",    analyze_risk_node)
    graph.add_node("inspect_app",     inspect_app_node)
    graph.add_node("gen_tests",       gen_tests_node)
    graph.add_node("run_playwright",  run_playwright_node)
    graph.add_node("detect_bugs",     detect_bugs_node)
    graph.add_node("log_bugs",        log_bugs_node)
    graph.add_node("summarize",       summarize_node)

    # ── Entry point ──────────────────────────────────────────────────────────
    graph.set_entry_point("fetch_ticket")

    # ── Linear edges ─────────────────────────────────────────────────────────
    graph.add_edge("fetch_ticket",   "analyze_risk")
    graph.add_edge("analyze_risk",   "inspect_app")
    graph.add_edge("inspect_app",    "gen_tests")
    graph.add_edge("gen_tests",      "run_playwright")
    graph.add_edge("run_playwright", "detect_bugs")

    # ── Conditional edge: after detect_bugs ──────────────────────────────────
    graph.add_conditional_edges(
        "detect_bugs",
        route_after_detect,
        {
            "log_bugs":  "log_bugs",
            "summarize": "summarize",
        }
    )

    # ── Terminal edges ───────────────────────────────────────────────────────
    graph.add_edge("log_bugs",  "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()
