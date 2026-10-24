"""Small deny-by-default policy layer evaluated before actions."""
PRIVILEGED_TERMS = ("grant access", "admin access", "disable security", "reset another user's password", "delete account")

def evaluate_action(action: str, query: str, user_id: str) -> dict:
    q = query.lower()
    if any(term in q for term in PRIVILEGED_TERMS):
        return {"decision": "approval_required", "reason": "privileged_action", "action": action, "user_id": user_id}
    if action not in {"create_ticket"}:
        return {"decision": "deny", "reason": "action_not_allowed_in_demo", "action": action, "user_id": user_id}
    return {"decision": "allow", "reason": "low_risk_demo_action", "action": action, "user_id": user_id}
