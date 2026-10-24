"""Central tool registry with typed metadata and approval flags."""
from typing import Callable, Any

TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "knowledge_search": {"description": "Search the frozen support-ticket knowledge set", "parameters": {"query": "string"}, "approval_required": False, "version": "1.0"},
    "account_status": {"description": "Read synthetic account status", "parameters": {"user_id": "string"}, "approval_required": False, "version": "1.0"},
    "create_ticket": {"description": "Create a local mock IT support ticket", "parameters": {"query": "string", "user_id": "string"}, "approval_required": False, "version": "1.0"},
    "grant_access": {"description": "Grant privileged access (not implemented in demo)", "parameters": {"user_id": "string", "resource": "string"}, "approval_required": True, "version": "1.0"},
}

def get_tool(name: str) -> dict[str, Any]:
    if name not in TOOL_REGISTRY: raise KeyError(f"Tool not registered: {name}")
    return TOOL_REGISTRY[name]

def list_tools() -> list[dict[str, Any]]:
    return [{"name": name, **metadata} for name, metadata in TOOL_REGISTRY.items()]
