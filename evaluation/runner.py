"""Run repeatable evaluation against a frozen CSV subset."""
import csv, time
from pathlib import Path
from config import get_settings
from graph import run_query
from evaluation.metrics import token_overlap, groundedness

def run_evaluation(limit: int | None = None) -> dict:
    path = Path(get_settings().data_path)
    if not path.exists(): return {"error": f"Golden dataset not found: {path}"}
    with path.open(encoding="utf-8-sig", newline="") as f: rows = list(csv.DictReader(f))
    if limit: rows = rows[:limit]
    if not rows: return {"error": "Golden dataset is empty"}
    results=[]; started=time.perf_counter()
    for i,row in enumerate(rows):
        query=row.get("initial_message", "").strip(); reference=row.get("resolution_summary", "").strip()
        if not query: continue
        t0=time.perf_counter(); output=run_query(query, "evaluation-user"); latency=round(time.perf_counter()-t0, 3)
        answer=output.get("final_answer", "")
        results.append({"ticket_id":row.get("ticket_id", str(i)), "correctness":token_overlap(answer, reference), "groundedness":groundedness(answer, output.get("retrieved_docs", [])), "ticket_created":bool(output.get("ticket")), "latency_seconds":latency})
    n=max(1,len(results))
    return {"dataset":str(path), "cases":len(results), "mean_correctness":round(sum(x["correctness"] for x in results)/n,3), "mean_groundedness":round(sum(x["groundedness"] for x in results)/n,3), "ticket_creation_rate":round(sum(x["ticket_created"] for x in results)/n,3), "mean_latency_seconds":round(sum(x["latency_seconds"] for x in results)/n,3), "wall_time_seconds":round(time.perf_counter()-started,3), "results":results}
