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
    page_title="Darwin: HR Observability Engine",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Premium & Dark-Mode Friendly Layout Styling
st.markdown(
    """
    <style>
    /* Styling for glassmorphic cards */
    .metric-card {
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .agent-tag {
        background-color: rgba(66, 135, 245, 0.15);
        color: #4287f5;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85em;
        margin-right: 6px;
        border: 1px solid rgba(66, 135, 245, 0.25);
    }
    .bypass-tag {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85em;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .memory-badge {
        background-color: rgba(139, 92, 246, 0.15);
        color: #8b5cf6;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 500;
        border: 1px solid rgba(139, 92, 246, 0.25);
    }
    .timeline-step {
        border-left: 2px solid rgba(255, 255, 255, 0.2);
        padding-left: 15px;
        padding-bottom: 15px;
        position: relative;
    }
    .timeline-step::before {
        content: '';
        width: 10px;
        height: 10px;
        background-color: #4287f5;
        border-radius: 50%;
        position: absolute;
        left: -6px;
        top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown("## 🧬 Darwin Agentic HR Observability Dashboard")
st.caption(
    "Production-grade Multi-Agent HR Workflow Engine | Cost Optimizer | Real-time Observability"
)

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "total_naive_cost" not in st.session_state:
    st.session_state.total_naive_cost = 0.0

if "total_optimized_cost" not in st.session_state:
    st.session_state.total_optimized_cost = 0.0

# Sidebar controls and configuration metadata
with st.sidebar:
    st.image("https://img.icons8.com/isometric-line/100/control-panel.png", width=60)
    st.subheader("Session Controls")
    st.text_input("Active Session ID", value=st.session_state.session_id, disabled=True)

    if st.button("Reset Session & Telemetry"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.session_state.total_naive_cost = 0.0
        st.session_state.total_optimized_cost = 0.0
        st.success("Session state cleared successfully!")
        st.rerun()

    st.markdown("---")
    st.subheader("System Metadata")
    st.markdown(f"**Environment:** `{settings.app_env.upper()}`")
    st.markdown(f"**API Gateway:** `{settings.backend_base_url}`")
    st.markdown(f"**Vector Store:** `ChromaDB` (`{settings.chroma_collection_name}`)")
    st.markdown(f"**SQLite Database:** `{settings.sqlite_path.name}`")
    st.markdown(f"**Model configuration:** `{settings.openai_model}`")

# Calculate metrics summary
total_naive = st.session_state.total_naive_cost
total_opt = st.session_state.total_optimized_cost
savings_percent = ((total_naive - total_opt) / total_naive) * 100 if total_naive > 0 else 0.0

# Session Statistics Cards
st.markdown("### 📊 Session Statistics")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="Total Naive Cost", value=f"${total_naive:.6f}")
with m2:
    st.metric(label="Total Optimized Cost", value=f"${total_opt:.6f}")
with m3:
    st.metric(
        label="Token Savings",
        value=f"{savings_percent:.1f}%",
        delta=f"-{savings_percent:.1f}%" if savings_percent > 0 else None,
        delta_color="normal",
    )

st.markdown("---")

# Main Dashboard Grid
col_chat, col_telemetry = st.columns([3, 2])

with col_chat:
    st.markdown("### 💬 Conversational Workspace")

    # Render previous messages from history
    for chat in st.session_state.chat_history:
        with st.chat_message("user", avatar="👤"):
            st.write(chat["user_input"])
        with st.chat_message("assistant", avatar="🧬"):
            st.write(chat["summary"])

            # Show executing agent badges
            if chat.get("executed_agents"):
                badges = "".join(
                    [f'<span class="agent-tag">{a}</span>' for a in chat["executed_agents"]]
                )
                st.markdown(f"**Agents:** {badges}", unsafe_allow_html=True)

            # Show context memory variables
            mem_vars = []
            if chat.get("employee_id"):
                mem_vars.append(f"Employee ID: `{chat['employee_id']}`")
            if chat.get("start_date") and chat.get("end_date"):
                mem_vars.append(f"Dates: `{chat['start_date']}` to `{chat['end_date']}`")
            if mem_vars:
                st.markdown(f"🧠 **Persisted Memory Context:** {' | '.join(mem_vars)}")

    # Chat input
    user_query = st.chat_input("Query employee leave, balances, or payslips...")

    if user_query:
        # Render user message instantly
        with st.chat_message("user", avatar="👤"):
            st.write(user_query)

        # Trigger API Invoke request
        payload = {"user_input": user_query, "session_id": st.session_state.session_id}
        try:
            response = requests.post(
                f"{settings.backend_base_url}/api/v1/workflows/invoke",
                json=payload,
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

            # Process responses
            action_result = data.get("action_result")
            policy_result = data.get("policy_result")

            summary = ""
            if action_result:
                summary = action_result.get("summary", "")
            elif policy_result:
                summary = policy_result.get("answer", "")
            else:
                summary = (
                    "Request was processed successfully (no database or policy changes needed)."
                )

            # Update costs
            st.session_state.total_naive_cost += data.get("naive_cost", 0.0)
            st.session_state.total_optimized_cost += data.get("optimized_cost", 0.0)

            # Append to session history
            st.session_state.chat_history.append(
                {
                    "user_input": user_query,
                    "summary": summary,
                    "executed_agents": data.get("executed_agents", []),
                    "employee_id": data.get("employee_id"),
                    "start_date": data.get("start_date"),
                    "end_date": data.get("end_date"),
                    "naive_cost": data.get("naive_cost", 0.0),
                    "optimized_cost": data.get("optimized_cost", 0.0),
                    "percentage_reduction": data.get("percentage_reduction", 0.0),
                    "route_decision": data.get("route_decision", {}),
                    "policy_result": policy_result,
                    "action_result": action_result,
                    "graph_visualization": data.get("graph_visualization"),
                    "latency_sec": data.get("latency_sec", 0.0),
                    "prompt_tokens": data.get("prompt_tokens", 0),
                    "completion_tokens": data.get("completion_tokens", 0),
                }
            )
            st.rerun()
        except Exception as e:
            st.error(f"Failed to communicate with API gateway: {e}")

with col_telemetry:
    st.markdown("### 🔍 Real-Time Telemetry & Observability")

    if st.session_state.chat_history:
        last_turn = st.session_state.chat_history[-1]

        # 1. Agent Status Badges
        st.markdown("**Active Step Status**")
        status_cols = st.columns(2)
        with status_cols[0]:
            if last_turn.get("policy_result"):
                status = last_turn["policy_result"].get("status", "unavailable")
                if status == "grounded":
                    st.success("🟢 Policy Agent: Answered")
                else:
                    st.error("🔴 Policy Agent: Not Found")
            else:
                st.markdown("⚪ Policy Agent: Inactive")

        with status_cols[1]:
            if last_turn.get("action_result"):
                status = last_turn["action_result"].get("status", "unknown")
                if status in ["approved", "success"]:
                    st.success("🟢 Action Agent: Approved")
                elif status in ["fallback", "fallback_queued"]:
                    st.warning("🟡 Action Agent: Cache Fallback")
                else:
                    st.error(f"🔴 Action Agent: Failed ({status})")
            else:
                st.markdown("⚪ Action Agent: Inactive")

        # 2. Token & Execution Cost details
        with st.expander("⏱️ Latency & Execution Cost", expanded=True):
            tc1, tc2 = st.columns(2)
            tc1.metric("Turn Latency", f"{last_turn.get('latency_sec', 0.0):.3f}s")
            cost_reduction = last_turn.get("percentage_reduction", 0.0)
            tc2.metric("Turn Token Savings", f"{cost_reduction:.1f}%")

            st.markdown("---")
            st.markdown(
                f"**Token Metrics:** `Prompt: {last_turn.get('prompt_tokens', 0)}` | "
                f"`Completion: {last_turn.get('completion_tokens', 0)}`"
            )

        # 3. Dynamic Execution Routing & Bypass Trace
        with st.expander("🧭 Execution Routing Trace", expanded=True):
            route_dec = last_turn.get("route_decision", {})
            rationale = route_dec.get("rationale", "")

            if "Bypassed LLM" in rationale:
                st.markdown(
                    'Strategy: <span class="bypass-tag">Deterministic Bypass</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    'Strategy: <span class="agent-tag">Supervisor LLM Decision</span>',
                    unsafe_allow_html=True,
                )

            st.markdown(f"**Rationale:** *{rationale}*")
            exec_path = " ➡️ ".join(last_turn["executed_agents"])
            st.markdown(f"**Orchestration Path:** `START` ➡️ `{exec_path}` ➡️ `END`")

        # 4. Tool Execution Timeline Details
        if last_turn.get("action_result"):
            with st.expander("🛠️ Resilient Tool Execution Timeline", expanded=False):
                act = last_turn["action_result"]
                tool_out = act.get("output", {})
                trace_meta = (
                    tool_out.get("trace_metadata", {}) if isinstance(tool_out, dict) else {}
                )

                st.markdown(
                    "<div class='timeline-step'><b>Node Spawning:</b> action_agent</div>",
                    unsafe_allow_html=True,
                )
                tool_name = act.get("tool")
                st.markdown(
                    f"<div class='timeline-step'><b>Tool Call:</b> <code>{tool_name}</code></div>",
                    unsafe_allow_html=True,
                )

                if isinstance(trace_meta, dict):
                    latency_t = trace_meta.get("latency_sec", 0.0)
                    retries = trace_meta.get("retries", 0)
                    st.markdown(
                        f"<div class='timeline-step'><b>Latency:</b> "
                        f"<code>{latency_t:.3f}s</code></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div class='timeline-step'><b>Retries:</b> <code>{retries}</code></div>",
                        unsafe_allow_html=True,
                    )

                    failures = trace_meta.get("failures", [])
                    if failures:
                        failures_list = "".join([f"<li><code>{f}</code></li>" for f in failures])
                        st.markdown(
                            f"<div class='timeline-step'><b>Errors:</b> "
                            f"<ul>{failures_list}</ul></div>",
                            unsafe_allow_html=True,
                        )

                status_code = act.get("status")
                st.markdown(
                    f"<div class='timeline-step'><b>Finalized:</b> "
                    f"Status <code>{status_code}</code></div>",
                    unsafe_allow_html=True,
                )

        # 5. Retrieved Documents & Similarity Ranks
        if last_turn.get("policy_result"):
            with st.expander("📚 Retrieved Knowledge Citations", expanded=False):
                citations = last_turn["policy_result"].get("citations", [])
                if citations:
                    for cit in citations:
                        st.markdown(
                            f"📁 **Section:** {cit.get('title')}\n"
                            f"- *Source Document:* `{cit.get('source')}`\n"
                            f"- *Relevance Rank:* `{cit.get('rank')}`"
                        )
                else:
                    st.write("No documents matched the query intent.")

        # 6. Graph Visualizations
        if last_turn.get("graph_visualization"):
            with st.expander("🕸️ Orchestration Graph Topology", expanded=False):
                st.code(last_turn["graph_visualization"], language="mermaid")
    else:
        st.info("Ask the Assistant a question to view agent execution traces and cost metrics.")
