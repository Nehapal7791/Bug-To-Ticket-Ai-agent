from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import QAState
from config import GROQ_MODEL
import json

llm = None


def get_llm():
    global llm
    if llm is None:
        llm = ChatGroq(model=GROQ_MODEL, temperature=0.2)
    return llm


def analyze_risk_node(state: QAState) -> QAState:
    """
    NODE 2: GPT analyzes the Jira ticket and assesses risk level.
    Returns a risk analysis and risk level (LOW/MEDIUM/HIGH).
    """
    prompt = f"""You are a senior QA engineer performing risk analysis.

Jira Ticket: {state['ticket_id']}
Summary: {state['ticket_summary']}
Description: {state['ticket_description']}
Acceptance Criteria: {state['ticket_acceptance_criteria']}
App URL: {state['app_url']}

Analyze this ticket and respond ONLY with a JSON object:
{{
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "risk_summary": "2-3 sentence risk assessment",
  "key_areas": ["list", "of", "areas", "to", "test"],
  "edge_cases": ["edge", "cases", "to", "cover"],
  "security_concerns": ["any", "security", "risks"]
}}"""

    response = get_llm().invoke([
        SystemMessage(content="You are a QA risk analysis expert. Respond only with valid JSON."),
        HumanMessage(content=prompt),
    ])

    try:
        # Strip markdown fences if present
        raw = response.content.strip().strip("```json").strip("```").strip()
        analysis = json.loads(raw)
    except Exception:
        analysis = {
            "risk_level": "MEDIUM",
            "risk_summary": response.content,
            "key_areas": ["general functionality"],
            "edge_cases": ["null inputs", "boundary values"],
            "security_concerns": [],
        }

    return {
        **state,
        "risk_analysis": json.dumps(analysis, indent=2),
        "risk_level":    analysis.get("risk_level", "MEDIUM"),
    }
