"""Small local retrieval index; swap with Chroma/FAISS for larger corpora."""
import csv
from pathlib import Path
from config import get_settings


def _load_rows():
    path = Path(get_settings().data_path)
    if not path.exists(): return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _tokens(text: str) -> set[str]:
    return {w.strip(".,!?():;\"'").lower() for w in text.split() if len(w) > 2}


def search_knowledge(query: str, _previous=None, limit: int = 3) -> list[dict]:
    rows = _load_rows()
    qtokens = _tokens(query)
    scored = []
    for row in rows:
        content = " ".join(str(row.get(k, "")) for k in ["initial_message", "agent_first_reply", "resolution_summary", "category"])
        tokens = _tokens(content)
        score = len(qtokens & tokens) / max(1, len(qtokens))
        if score > 0: scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    result = []
    for score, row in scored[:limit]:
        result.append({"ticket_id": row.get("ticket_id", ""), "category": row.get("category", ""), "initial_message": row.get("initial_message", ""), "resolution_summary": row.get("resolution_summary", ""), "score": round(score, 3), "source": "golden_it_support_tickets.csv"})
    return result
