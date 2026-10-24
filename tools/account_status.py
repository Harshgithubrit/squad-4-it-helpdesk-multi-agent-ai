"""Mock account-status tool. Replace with an authorized identity provider integration."""
from datetime import datetime, timezone

def get_account_status(user_id: str) -> dict:
    # Deliberately synthetic data. Do not connect this demo to production identity systems.
    return {"user_id": user_id, "status": "active", "mfa_enabled": True, "checked_at": datetime.now(timezone.utc).isoformat(), "source": "mock_directory"}
