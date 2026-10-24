from tools.create_ticket import create_ticket
from security.policy_engine import evaluate_action
from observability.tracing import traced

@traced("agent.action_ticket")
def action_ticket_agent(state: dict) -> dict:
    decision = evaluate_action("create_ticket", state.get("query", ""), state.get("user_id", "demo-user-001"))
    if decision["decision"] == "deny":
        return {"final_answer": "I cannot perform that action because it violates the helpdesk policy. Please contact an authorized administrator.", "decision": "denied", "current_agent": "action_ticket", "tool_results": state.get("tool_results", []) + [{"tool": "policy_engine", "result": decision}]}
    if decision["decision"] == "approval_required" and not state.get("approval_granted", False):
        return {"needs_approval": True, "final_answer": "This request involves a privileged action. Human approval is required before proceeding. No privileged change has been performed.", "decision": "approval_required", "current_agent": "action_ticket", "tool_results": state.get("tool_results", []) + [{"tool": "policy_engine", "result": decision}]}
    ticket = create_ticket(state.get("query", ""), state.get("user_id", "demo-user-001"), state.get("retrieved_docs", []))
    return {"ticket": ticket, "final_answer": (state.get("final_answer", "") + "\n\nA support ticket has been created for follow-up.").strip(), "decision": "ticket_created", "current_agent": "action_ticket", "tool_results": state.get("tool_results", []) + [{"tool": "create_ticket", "result": ticket}]}
