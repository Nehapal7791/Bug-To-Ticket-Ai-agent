from graph.state import QAState


def self_heal_node(state: QAState) -> QAState:
    """
    NODE 6 (loop): Increment retry counter.
    The graph routes back to gen_tests with DOM snapshot context.
    GPT will use the DOM snapshot to regenerate tests with correct selectors.
    """
    return {
        **state,
        "retry_count":       state.get("retry_count", 0) + 1,
        "playwright_script": "",    # cleared so gen_tests regenerates
        "test_results":      [],    # cleared for fresh run
        "execution_error":   None,
    }
