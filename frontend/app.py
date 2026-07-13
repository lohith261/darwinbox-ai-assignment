"""Streamlit frontend dashboard for real-time workflow monitoring and observability metrics."""

import sys
import uuid
from pathlib import Path

import requests

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st

from backend.config.settings import get_settings

settings = get_settings()

st.set_page_config(
    page_title="Darwinbox AI Observability Engine",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom premium styling
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .agent-tag {
        background-color: #e2eafc;
        color: #1e3a8a;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.85em;
        margin-right: 5px;
    }
    .bypass-tag {
        background-color: #d1fae5;
        color: #065f46;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.85em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧭 Darwinbox AI Workflow Engine")
st.caption("Agentic HR Workflow Orchestrator with Production Observability & Cost Optimization")

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "total_naive_cost" not in st.session_state:
    st.session_state.total_naive_cost = 0.0

if "total_optimized_cost" not in st.session_state:
    st.session_state.total_optimized_cost = 0.0

# Sidebar configuration
with st.sidebar:
    st.header("Session Settings")
    st.text_input("Active Session ID", value=st.session_state.session_id, disabled=True)
    if st.button("Reset Session & Cost Metrics"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.session_state.total_naive_cost = 0.0
        st.session_state.total_optimized_cost = 0.0
        st.rerun()

    st.markdown("---")
    st.subheader("System Metadata")
    st.write(
        {
            "Environment": settings.app_env,
            "Backend API": settings.backend_base_url,
            "SQLite Path": str(settings.sqlite_path.name),
            "Chroma Path": str(settings.chroma_persist_directory.name),
        }
    )

# Main Layout
col_chat, col_obs = st.columns([3, 2])

with col_chat:
    st.subheader("Conversational Assistant")

    # Render chat messages from history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["user_input"])
        with st.chat_message("assistant"):
            st.write(chat["summary"])
            if chat.get("executed_agents"):
                agents_html = "".join(
                    [f'<span class="agent-tag">{a}</span>' for a in chat["executed_agents"]]
                )
                st.markdown(f"**Executed Agents:** {agents_html}", unsafe_allow_html=True)

            # Show context memory variables
            mem_vars = []
            if chat.get("employee_id"):
                mem_vars.append(f"Employee ID: `{chat['employee_id']}`")
            if chat.get("start_date") and chat.get("end_date"):
                mem_vars.append(f"Dates: `{chat['start_date']}` to `{chat['end_date']}`")
            if mem_vars:
                st.markdown(f"🧠 **Persisted Memory Context:** {' | '.join(mem_vars)}")

    # Chat input
    user_query = st.chat_input("Ask about leave policies, salary, or balance...")

    if user_query:
        # Append user query to chat instantly
        with st.chat_message("user"):
            st.write(user_query)

        # Trigger Backend Workflow API Call
        payload = {"user_input": user_query, "session_id": st.session_state.session_id}

        try:
            response = requests.post(
                f"{settings.backend_base_url}/api/v1/workflows/invoke", json=payload, timeout=15.0
            )
            response.raise_for_status()
            data = response.json()

            # Format and parse final response summary
            route_decision = data.get("route_decision", {})
            executed_agents = data.get("executed_agents", [])
            action_result = data.get("action_result")
            policy_result = data.get("policy_result")

            summary = ""
            if action_result:
                summary = action_result.get("summary", "")
            elif policy_result:
                summary = policy_result.get("answer", "")
            else:
                summary = "I was routed, but no action or policy response was returned."

            # Update accumulated session costs
            naive_cost = data.get("naive_cost", 0.0)
            optimized_cost = data.get("optimized_cost", 0.0)
            st.session_state.total_naive_cost += naive_cost
            st.session_state.total_optimized_cost += optimized_cost

            # Save to chat history
            chat_record = {
                "user_input": user_query,
                "summary": summary,
                "executed_agents": executed_agents,
                "employee_id": data.get("employee_id"),
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "naive_cost": naive_cost,
                "optimized_cost": optimized_cost,
                "percentage_reduction": data.get("percentage_reduction", 0.0),
                "route_decision": route_decision,
                "policy_result": policy_result,
                "action_result": action_result,
                "graph_visualization": data.get("graph_visualization"),
                "latency_sec": data.get("latency_sec", 0.0),
                "prompt_tokens": data.get("prompt_tokens", 0),
                "completion_tokens": data.get("completion_tokens", 0),
            }
            st.session_state.chat_history.append(chat_record)
            st.rerun()

        except Exception as e:
            st.error(f"Error communicating with backend workflow API: {e}")

# Observability Panel
with col_obs:
    st.subheader("Observability & Optimization Metrics")

    if st.session_state.chat_history:
        last_chat = st.session_state.chat_history[-1]

        # Cost savings calculation
        total_naive = st.session_state.total_naive_cost
        total_opt = st.session_state.total_optimized_cost
        total_reduction = (
            ((total_naive - total_opt) / total_naive) * 100 if total_naive > 0 else 0.0
        )

        # Status Indicators
        st.markdown("**Status Overview**")
        if last_chat.get("action_result"):
            act_status = last_chat["action_result"].get("status", "unknown")
            if act_status in ["approved", "success"]:
                st.success("🟢 Action Completed: Success")
            elif act_status in ["fallback", "fallback_queued"]:
                st.warning(f"🟡 Action Completed: Cached/Queued ({act_status})")
            else:
                st.error(f"🔴 Action Completed: Failed ({act_status})")
        elif last_chat.get("policy_result"):
            pol_ans = last_chat["policy_result"].get("answer", "").lower()
            if "policy is unavailable" in pol_ans or "policy unavailable" in pol_ans:
                st.error("🔴 Policy Search: Information Unavailable")
            else:
                st.success("🟢 Policy Search: Answered")
        else:
            st.info("⚪ Session Started")

        # Routing Trace Panel
        with st.expander("🧭 Execution Agent Routing Trace", expanded=True):
            st.write(f"**Executed Path:** {' ➡️ '.join(last_chat['executed_agents'])}")
            rd = last_chat.get("route_decision", {})
            rationale = rd.get("rationale", "")

            if "Bypassed LLM" in rationale:
                st.markdown(
                    'Routing Strategy: <span class="bypass-tag">Deterministic Bypass</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    'Routing Strategy: <span class="agent-tag">LLM Router</span>',
                    unsafe_allow_html=True,
                )

        # Metrics Panel
        with st.expander("📊 Latency, Token & Cost Metrics", expanded=True):
            st.markdown("**Session Token Optimization**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Session Naive Cost", f"${total_naive:.6f}")
            c2.metric("Session Optimized Cost", f"${total_opt:.6f}")
            c3.metric(
                "Session Savings",
                f"{total_reduction:.1f}%",
                delta=f"-{total_reduction:.1f}%" if total_reduction > 0 else None,
                delta_color="normal",
            )

            st.markdown("---")
            st.markdown("**Current Turn metrics**")
            col_l, col_t = st.columns(2)
            with col_l:
                st.write(f"⏱️ **Latency:** `{last_chat.get('latency_sec', 0.0):.3f}s`")
            with col_t:
                st.write(
                    f"🔢 **Tokens:** `Prompt: {last_chat.get('prompt_tokens', 0)}` | "
                    f"`Completion: {last_chat.get('completion_tokens', 0)}`"
                )

        # Retrieved Documents Panel
        if last_chat.get("policy_result"):
            with st.expander("🔍 Retrieved Policy Documents", expanded=False):
                cits = last_chat["policy_result"].get("citations", [])
                if cits:
                    for c in cits:
                        st.markdown(
                            f"- **{c.get('title')}**\n"
                            f"  *Source:* `{c.get('source')}` | *Rank:* `{c.get('rank')}`"
                        )
                else:
                    st.write("No documents were retrieved.")

        # Tool Execution Panel
        if last_chat.get("action_result"):
            with st.expander("🛠️ Resilient Tool Execution Logs", expanded=False):
                act = last_chat["action_result"]
                tool_out = act.get("output", {})
                trace_meta = (
                    tool_out.get("trace_metadata", {}) if isinstance(tool_out, dict) else {}
                )

                st.write(f"⚙️ **Executed Tool:** `{act.get('tool')}`")
                st.write(f"📈 **Status Code:** `{act.get('status')}`")

                if isinstance(trace_meta, dict):
                    st.write(f"⏱️ **Tool Latency:** `{trace_meta.get('latency_sec', 0.0):.3f}s`")
                    st.write(f"🔄 **Retry Attempts:** `{trace_meta.get('retries', 0)}`")
                    failures = trace_meta.get("failures", [])
                    if failures:
                        st.write("❌ **Logged Failures:**")
                        for f in failures:
                            st.write(f"  - `{f}`")

        # Topology Panel
        with st.expander("🕸️ Graph Topology", expanded=False):
            gv = last_chat.get("graph_visualization")
            if gv:
                st.code(gv, language="mermaid")
    else:
        st.info("Enter a query in the chat assistant to display execution traces and cost metrics.")
