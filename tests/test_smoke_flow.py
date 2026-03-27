from unittest.mock import patch

from main import run_agent


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def invoke(self, messages):
        prompt = messages[-1].content

        if "Analyze this ticket and respond ONLY with a JSON object" in prompt:
            return FakeResponse(
                '{"risk_level":"MEDIUM","risk_summary":"Checkout flow has moderate risk.","key_areas":["login","cart","checkout"],"edge_cases":["invalid login","empty cart"],"security_concerns":["auth"]}'
            )

        if "Generate test cases and a Playwright script" in prompt:
            return FakeResponse(
                '{'
                '"test_cases":['
                '{"id":"TC001","name":"Login works","category":"functional","steps":["Open app","Login"],"expected":"User reaches inventory","priority":"HIGH"},'
                '{"id":"TC002","name":"Add to cart works","category":"functional","steps":["Add item"],"expected":"Cart count updates","priority":"MEDIUM"}'
                '],'
                '"playwright_script":"import time\nfrom playwright.sync_api import sync_playwright\nwith sync_playwright() as p:\n    browser = p.chromium.launch()\n    page = browser.new_page()\n    try:\n        _record(\"TC001 - Login works\", True)\n    except Exception as e:\n        _record(\"TC001 - Login works\", False, error=str(e))\n    try:\n        _record(\"TC002 - Add to cart works\", True)\n    except Exception as e:\n        _record(\"TC002 - Add to cart works\", False, error=str(e))\n    browser.close()"'
                '}'
            )

        if "Classify these test failures" in prompt:
            return FakeResponse('{"bugs":[],"has_selector_issues":false,"has_real_bugs":false}')

        return FakeResponse(
            "All mocked tests passed. No real bugs were found. The feature appears stable enough for further validation or deployment."
        )


MOCK_TICKET = {
    "id": "QA-42",
    "summary": "Validate checkout happy path",
    "description": "As a user I should be able to login and add an item to the cart.",
    "acceptance_criteria": "User can login and add a product to cart successfully.",
    "issue_type": "Story",
    "status": "To Do",
    "priority": "High",
}

MOCK_INSPECTION = {
    "login_detected": True,
    "login_attempted": False,
    "login_success_likely": False,
    "username_selector": "input[name='email']",
    "password_selector": "input[name='password']",
    "submit_candidates": ["button[type='submit']"],
    "vertical_candidates": [],
    "project_candidates": [],
    "elements_before_login": [],
    "elements_after_login": [],
    "notes": ["Mock inspection"],
    "artifact_path": "reports/inspection/mock.json",
}


MOCK_RESULTS = {
    "status": "PASS",
    "total": 2,
    "passed": 2,
    "failed": 0,
    "tests": [
        {"name": "TC001 - Login works", "passed": True, "error": None, "details": ""},
        {"name": "TC002 - Add to cart works", "passed": True, "error": None, "details": ""},
    ],
}


def test_smoke_flow_runs_end_to_end(capsys):
    with patch("graph.nodes.analyze_risk.llm", FakeLLM()), patch("graph.nodes.gen_tests.llm", FakeLLM()), patch("graph.nodes.detect_bugs.llm", FakeLLM()), patch("graph.nodes.summarize.llm", FakeLLM()), patch("graph.nodes.fetch_ticket.jira_fetch", return_value=MOCK_TICKET), patch("graph.nodes.inspect_app.inspect_application", return_value=MOCK_INSPECTION), patch("graph.nodes.run_playwright.run_playwright_script", return_value=MOCK_RESULTS), patch("graph.nodes.run_playwright.capture_dom_snapshot", return_value="[]"), patch("graph.nodes.log_bugs.create_bug_ticket", return_value="https://jira.example/browse/QA-999"):
        run_agent("QA-42", "https://www.saucedemo.com")

    output = capsys.readouterr().out
    assert "Running QA Agent" in output
    assert "Fetching Jira ticket" in output
    assert "Generating report" in output
