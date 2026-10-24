from tools.account_status import get_account_status
from observability.tracing import traced

@traced("agent.access_check")
def access_check_agent(state: dict) -> dict:
    status = get_account_status(state.get("user_id", "demo-user-001"))
    return {"tool_results": state.get("tool_results", []) + [{"tool": "account_status", "result": status}], "current_agent": "access_check"}
