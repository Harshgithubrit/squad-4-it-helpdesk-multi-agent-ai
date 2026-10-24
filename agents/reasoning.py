from observability.tracing import traced

@traced("agent.reasoning")
def reasoning_agent(state: dict) -> dict:
    q = state.get("query", "").lower()
    docs = state.get("retrieved_docs", [])
    plan = []
    if any(k in q for k in ["access", "login", "locked", "account", "password", "permission", "grant"]):
        plan = ["Check account status", "Provide safe troubleshooting steps", "Escalate access changes for approval if required"]
    elif any(k in q for k in ["network", "wifi", "internet", "vpn"]):
        plan = ["Check network troubleshooting guidance", "Ask user to verify connectivity and VPN", "Create a support ticket if unresolved"]
    elif any(k in q for k in ["laptop", "hardware", "keyboard", "monitor", "printer"]):
        plan = ["Check hardware troubleshooting guidance", "Collect device details if unresolved", "Create a support ticket"]
    else:
        plan = ["Search known support guidance", "Give grounded next steps", "Create a ticket if the issue remains unresolved"]
    answer = docs[0]["resolution_summary"] if docs else "I could not find a matching article in the demo knowledge base. I can create a ticket so the IT team can investigate."
    return {"plan": plan, "decision": "approval_required" if any(k in q for k in ["grant access", "admin access", "reset another user's password", "disable security"]) else "continue", "tool_results": state.get("tool_results", []) + [{"tool": "reasoning", "plan": plan}], "current_agent": "reasoning", "final_answer": answer}
