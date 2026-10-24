"""Creates a local mock ticket; no external service is contacted."""
from datetime import datetime, timezone
from uuid import uuid4

def create_ticket(query: str, user_id: str, docs: list[dict]) -> dict:
    return {"ticket_id": "HD-" + uuid4().hex[:8].upper(), "user_id": user_id, "summary": query[:160], "priority": "medium", "status": "open", "related_articles": [d.get("ticket_id") for d in docs], "created_at": datetime.now(timezone.utc).isoformat(), "mode": "mock"}
