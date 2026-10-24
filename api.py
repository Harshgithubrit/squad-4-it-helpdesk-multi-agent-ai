"""FastAPI entry point with dependency-injected authentication and authorization."""
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from security.auth import (
    ACCESS_TOKEN_MINUTES, Principal, authenticate_user, create_access_token,
    get_current_user, require_roles,
)
from dependencies import get_helpdesk_graph
from schemas import HelpdeskRequest, HelpdeskResponse, LoginRequest, TokenResponse
from uuid import uuid4
from time import time
from observability.tracing import span

app = FastAPI(
    title="Squad-4 IT Helpdesk Multi-Agent API",
    version="1.0.0",
    description="Authenticated helpdesk API with role-based authorization and Pydantic validation.",
)

@app.post("/auth/token", response_model=TokenResponse, tags=["authentication"])
def issue_token(form: OAuth2PasswordRequestForm = Depends()):
    principal = authenticate_user(form.username, form.password)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    return TokenResponse(access_token=create_access_token(principal), expires_in=ACCESS_TOKEN_MINUTES * 60)

@app.post("/auth/login", response_model=TokenResponse, tags=["authentication"])
def login(body: LoginRequest):
    """JSON-based login alternative for clients that do not use OAuth form encoding."""
    principal = authenticate_user(body.username, body.password)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return TokenResponse(access_token=create_access_token(principal), expires_in=ACCESS_TOKEN_MINUTES * 60)

@app.get("/auth/me", tags=["authentication"])
def who_am_i(principal: Principal = Depends(get_current_user)):
    return {"user_id": principal.user_id, "username": principal.username, "roles": principal.roles}

@app.post("/helpdesk/query", response_model=HelpdeskResponse, tags=["helpdesk"])
def submit_query(
    body: HelpdeskRequest,
    principal: Principal = Depends(get_current_user),
    graph=Depends(get_helpdesk_graph),
):
    """Any authenticated user may submit an issue; identity comes from the token, not request JSON."""
    session_id = body.session_id or str(uuid4())
    initial = {
        "messages": [{"role": "user", "content": body.query}],
        "query": body.query,
        "user_id": principal.user_id,
        "username": principal.username,
        "roles": principal.roles,
        "session_id": session_id,
        "current_agent": "", "tool_results": [], "retrieved_docs": [], "plan": [],
        "needs_approval": False, "approval_granted": False, "ticket": None,
        "final_answer": "", "decision": "", "error": None, "started_at": time(),
    }
    with span("helpdesk.request", {"user.id": principal.user_id}):
        result = graph.invoke(initial)
    return HelpdeskResponse(
        session_id=result.get("session_id", session_id), user_id=principal.user_id,
        final_answer=result.get("final_answer", "No answer generated."),
        decision=result.get("decision", "unknown"), needs_approval=result.get("needs_approval", False),
        ticket=result.get("ticket"), tool_results=result.get("tool_results", []),
    )

@app.get("/admin/tools", tags=["administration"])
def list_registered_tools(principal: Principal = Depends(require_roles("admin"))):
    from tools.registry import list_tools
    return {"requested_by": principal.username, "tools": list_tools()}

@app.get("/health", tags=["operations"])
def health():
    return {"status": "ok", "service": "squad-4-it-helpdesk"}
