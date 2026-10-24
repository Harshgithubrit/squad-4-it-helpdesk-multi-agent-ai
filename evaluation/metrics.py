"""Simple transparent evaluation metrics for the frozen golden set."""
def token_overlap(prediction: str, reference: str) -> float:
    p = {x.lower().strip(".,!?;:") for x in prediction.split() if len(x) > 2}
    r = {x.lower().strip(".,!?;:") for x in reference.split() if len(x) > 2}
    return round(len(p & r) / max(1, len(r)), 3)

def groundedness(prediction: str, retrieved_docs: list[dict]) -> float:
    evidence = " ".join(d.get("resolution_summary", "") for d in retrieved_docs)
    return token_overlap(prediction, evidence) if evidence else 0.0
