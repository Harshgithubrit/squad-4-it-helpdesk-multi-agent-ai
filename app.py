"""Streamlit UI for the IT Helpdesk multi-agent demo."""
import json
import streamlit as st
from graph import build_graph
from config import get_settings
from observability.session_capture import load_sessions
from evaluation.runner import run_evaluation

st.set_page_config(page_title="Squad-4 | IT Helpdesk Agent", page_icon="🛠️", layout="wide")
st.title("🛠️ IT Helpdesk Multi-Agent System")
st.caption("Squad-4 • LangGraph orchestration • Policy controls • OpenTelemetry-ready traces")
settings = get_settings()
with st.sidebar:
    st.subheader("Configuration")
    st.write(f"LLM provider: `{settings.llm_provider}`")
    st.write(f"Model: `{settings.llm_model or 'mock / rules fallback'}`")
    st.info("Set ANTHROPIC_API_KEY or OPENAI_API_KEY and LLM_PROVIDER in .env to enable an LLM. The demo also runs without a key.")
    if st.button("Run golden-set evaluation", use_container_width=True):
        with st.spinner("Evaluating tickets..."):
            st.session_state["eval_result"] = run_evaluation()

query = st.text_area("Describe your IT issue", placeholder="Example: I cannot access my company account after a password reset.", height=110)
user_id = st.text_input("Demo user ID", value="demo-user-001")
if st.button("Submit helpdesk request", type="primary", disabled=not query.strip()):
    app = build_graph()
    initial = {"messages": [{"role": "user", "content": query.strip()}], "query": query.strip(), "user_id": user_id.strip() or "demo-user-001", "session_id": None, "current_agent": "", "tool_results": [], "retrieved_docs": [], "plan": [], "needs_approval": False, "approval_granted": False, "ticket": None, "final_answer": "", "decision": "", "error": None}
    with st.spinner("Agents are processing your request..."):
        result = app.invoke(initial)
    st.session_state["last_result"] = result

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    st.subheader("Assistant response")
    st.write(result.get("final_answer", "No answer was generated."))
    if result.get("needs_approval"):
        st.warning("This action requires human approval. No privileged change was executed.")
        if st.button("Approve demo action"):
            result["approval_granted"] = True
            result["needs_approval"] = False
            result["final_answer"] = "Approval recorded for this demo. Re-submit the request to continue the approved workflow."
            st.session_state["last_result"] = result
            st.rerun()
    if result.get("ticket"):
        st.success("Mock ticket created")
        st.json(result["ticket"])
    with st.expander("Execution details / tool results"):
        st.json({"session_id": result.get("session_id"), "decision": result.get("decision"), "current_agent": result.get("current_agent"), "tool_results": result.get("tool_results", []), "retrieved_docs": result.get("retrieved_docs", []), "plan": result.get("plan", []), "error": result.get("error")})

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Recent captured sessions")
    sessions = load_sessions(limit=10)
    if sessions: st.dataframe(sessions, use_container_width=True)
    else: st.caption("No sessions captured yet. Submit a request to create one.")
with right:
    st.subheader("Golden-set evaluation")
    if "eval_result" in st.session_state:
        st.json(st.session_state["eval_result"])
    else:
        st.caption("Run evaluation from the sidebar to score correctness, groundedness, tool use, and latency.")
