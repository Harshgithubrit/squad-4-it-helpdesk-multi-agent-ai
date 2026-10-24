"""LangGraph orchestration: route -> search/access -> reason -> policy/action -> capture."""
from uuid import uuid4
from time import time
from langgraph.graph import StateGraph, START, END
from state import HelpdeskState
from agents.knowledge_search import knowledge_search_agent
from agents.access_check import access_check_agent
from agents.reasoning import reasoning_agent
from agents.action_ticket import action_ticket_agent
from observability.tracing import traced, span
from observability.session_capture import capture_session

@traced("router.intent")
def route_intent(state: HelpdeskState) -> str:
    q = state.get("query", "").lower()
    if any(k in q for k in ["access", "login", "locked", "account", "password", "permission", "grant"]): return "access_check"
    return "knowledge_search"

def finalize(state: HelpdeskState) -> dict:
    if not state.get("final_answer"):
        state["final_answer"] = "I reviewed your issue. Please try the suggested steps, or use the created ticket to follow up with IT."
    state["current_agent"] = "finalize"
    capture_session(state, "approval_required" if state.get("needs_approval") else "completed")
    return {"current_agent": "finalize", "final_answer": state["final_answer"]}

def build_graph():
    graph = StateGraph(HelpdeskState)
    graph.add_node("knowledge_search", knowledge_search_agent)
    graph.add_node("access_check", access_check_agent)
    graph.add_node("reasoning", reasoning_agent)
    graph.add_node("action_ticket", action_ticket_agent)
    graph.add_node("finalize", finalize)
    graph.add_conditional_edges(START, route_intent, {"knowledge_search": "knowledge_search", "access_check": "access_check"})
    graph.add_edge("knowledge_search", "reasoning")
    graph.add_edge("access_check", "knowledge_search")
    graph.add_edge("reasoning", "action_ticket")
    graph.add_edge("action_ticket", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()

def run_query(query: str, user_id: str = "demo-user-001") -> dict:
    state: HelpdeskState = {"messages": [{"role": "user", "content": query}], "query": query, "user_id": user_id, "session_id": str(uuid4()), "current_agent": "", "tool_results": [], "retrieved_docs": [], "plan": [], "needs_approval": False, "approval_granted": False, "ticket": None, "final_answer": "", "decision": "", "error": None, "started_at": time()}
    with span("helpdesk.request", {"user.id": user_id}): return build_graph().invoke(state)
