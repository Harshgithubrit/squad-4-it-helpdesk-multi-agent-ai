from tools.knowledge_search import search_knowledge
from observability.tracing import traced

@traced("agent.knowledge_search")
def knowledge_search_agent(state: dict) -> dict:
    result = search_knowledge(state.get("query", ""), state.get("retrieved_docs", []))
    return {"retrieved_docs": result, "tool_results": state.get("tool_results", []) + [{"tool": "knowledge_search", "result_count": len(result)}], "current_agent": "knowledge_search"}
