"""Typed state shared by LangGraph nodes."""
from typing import Any, TypedDict

class HelpdeskState(TypedDict, total=False):
    messages: list[dict[str, str]]
    query: str
    user_id: str
    username: str
    roles: list[str]
    session_id: str
    current_agent: str
    tool_results: list[dict[str, Any]]
    retrieved_docs: list[dict[str, Any]]
    plan: list[str]
    needs_approval: bool
    approval_granted: bool
    ticket: dict[str, Any] | None
    final_answer: str
    decision: str
    error: str | None
    started_at: float
