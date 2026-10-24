from security.policy_engine import evaluate_action

def test_normal_ticket_allowed():
    assert evaluate_action("create_ticket", "Printer is offline", "u1")["decision"] == "allow"

def test_privileged_action_requires_approval():
    assert evaluate_action("create_ticket", "Please grant access to admin portal", "u1")["decision"] == "approval_required"

def test_unknown_action_denied():
    assert evaluate_action("delete_user", "delete user", "u1")["decision"] == "deny"
