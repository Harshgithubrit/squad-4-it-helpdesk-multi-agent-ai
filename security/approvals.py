"""Human-in-the-loop approval helpers."""
def approval_message(action: str) -> str:
    return f"Approval required for '{action}'. A human reviewer must authorize this action before execution."
