"""Append-only session capture for replay/debugging. Avoid storing secrets/PII."""
import json
from pathlib import Path
from datetime import datetime, timezone
from config import get_settings

def capture_session(state: dict, outcome: str = "completed") -> None:
    path = Path(get_settings().session_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = {k: state.get(k) for k in ["session_id", "query", "user_id", "current_agent", "tool_results", "retrieved_docs", "plan", "decision", "final_answer", "ticket", "error"]}
    record = {"captured_at": datetime.now(timezone.utc).isoformat(), "outcome": outcome, "state": safe}
    with path.open("a", encoding="utf-8") as f: f.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_sessions(limit: int = 20) -> list[dict]:
    path = Path(get_settings().session_path)
    if not path.exists(): return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            r = json.loads(line); s = r.get("state", {})
            rows.append({"captured_at": r.get("captured_at"), "session_id": s.get("session_id"), "query": s.get("query", "")[:90], "decision": s.get("decision"), "outcome": r.get("outcome")})
        except json.JSONDecodeError: continue
    return list(reversed(rows))

def get_capture(session_id: str) -> dict | None:
    path = Path(get_settings().session_path)
    if not path.exists(): return None
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        try:
            record = json.loads(line)
            if record.get("state", {}).get("session_id") == session_id: return record
        except json.JSONDecodeError: pass
    return None
