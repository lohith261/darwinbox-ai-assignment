import { useState } from "react";
import type { ChatTurn } from "../types";

interface TelemetryPanelProps {
  turn: ChatTurn | null;
  loading: boolean;
}

export default function TelemetryPanel({ turn, loading }: TelemetryPanelProps) {
  const [showGraph, setShowGraph] = useState(false);

  if (!turn && !loading) {
    return (
      <section className="telemetry-panel">
        <div className="panel-header">
          <h2>Real-Time Telemetry</h2>
        </div>
        <div className="telemetry-empty">
          <div className="telemetry-empty-icon">🔍</div>
          <p>Ask the assistant a question to view agent execution traces and cost metrics.</p>
        </div>
      </section>
    );
  }

  if (!turn) return null;

  const isBypass = turn.route_decision.rationale.includes("Bypassed LLM");
  const policyActive = turn.policy_result !== null;
  const actionActive = turn.action_result !== null;

  const policyStatus = turn.policy_result?.status;
  const actionStatus = turn.action_result?.status;

  const traceMeta =
    turn.action_result?.output &&
    typeof turn.action_result.output === "object" &&
    "trace_metadata" in turn.action_result.output
      ? (turn.action_result.output.trace_metadata as {
          latency_sec: number;
          retries: number;
          failures: string[];
        })
      : null;

  const citations = turn.policy_result?.citations ?? [];

  return (
    <section className="telemetry-panel">
      <div className="panel-header">
        <h2>Real-Time Telemetry</h2>
      </div>

      <div className="telemetry-scroll">
        {/* Agent Status */}
        <div className="telemetry-section">
          <h3 className="telemetry-label">Active Step Status</h3>
          <div className="status-grid">
            <div className={`status-card ${policyActive ? (policyStatus === "grounded" ? "status--success" : "status--error") : "status--idle"}`}>
              <span className="status-icon">
                {policyActive ? (policyStatus === "grounded" ? "🟢" : "🔴") : "⚪"}
              </span>
              <div>
                <div className="status-name">Policy Agent</div>
                <div className="status-detail">
                  {!policyActive ? "Inactive" : policyStatus === "grounded" ? "Answered" : "Not Found"}
                </div>
              </div>
            </div>

            <div className={`status-card ${actionActive ? (actionStatus === "success" || actionStatus === "approved" ? "status--success" : actionStatus?.includes("fallback") ? "status--warning" : "status--error") : "status--idle"}`}>
              <span className="status-icon">
                {actionActive ? (actionStatus === "success" || actionStatus === "approved" ? "🟢" : actionStatus?.includes("fallback") ? "🟡" : "🔴") : "⚪"}
              </span>
              <div>
                <div className="status-name">Action Agent</div>
                <div className="status-detail">
                  {!actionActive ? "Inactive" : actionStatus?.includes("fallback") ? "Cache Fallback" : actionStatus === "success" || actionStatus === "approved" ? "Approved" : `Failed (${actionStatus})`}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Latency & Cost */}
        <div className="telemetry-section">
          <h3 className="telemetry-label">Latency & Execution Cost</h3>
          <div className="metric-row">
            <div className="metric-box">
              <span className="metric-label">Turn Latency</span>
              <span className="metric-value">{turn.latency_sec.toFixed(3)}s</span>
            </div>
            <div className="metric-box">
              <span className="metric-label">Token Savings</span>
              <span className="metric-value">{turn.percentage_reduction.toFixed(1)}%</span>
            </div>
          </div>
          <div className="token-line">
            <span>Prompt: <code>{turn.prompt_tokens}</code></span>
            <span>Completion: <code>{turn.completion_tokens}</code></span>
          </div>
        </div>

        {/* Routing Trace */}
        <div className="telemetry-section">
          <h3 className="telemetry-label">Execution Routing Trace</h3>
          <div className="route-strategy">
            {isBypass ? (
              <span className="tag tag--bypass">Deterministic Bypass</span>
            ) : (
              <span className="tag tag--llm">Supervisor LLM Decision</span>
            )}
          </div>
          <p className="rationale">"{turn.route_decision.rationale}"</p>
          <div className="orchestration-path">
            <span className="path-node">START</span>
            {turn.executed_agents.map((a) => (
              <span key={a} className="path-arrow">➡️</span>
            ))}
            {turn.executed_agents.map((a) => (
              <span key={a} className="path-node">{a}</span>
            ))}
            <span className="path-arrow">➡️</span>
            <span className="path-node">END</span>
          </div>
        </div>

        {/* Tool Execution Timeline */}
        {turn.action_result && (
          <div className="telemetry-section">
            <h3 className="telemetry-label">Resilient Tool Execution Timeline</h3>
            <div className="timeline">
              <div className="timeline-step">
                <div className="timeline-dot" />
                <div className="timeline-content">
                  <strong>Node Spawning:</strong> <code>action_agent</code>
                </div>
              </div>
              <div className="timeline-step">
                <div className="timeline-dot" />
                <div className="timeline-content">
                  <strong>Tool Call:</strong> <code>{turn.action_result.tool}</code>
                </div>
              </div>
              {traceMeta && (
                <>
                  <div className="timeline-step">
                    <div className="timeline-dot" />
                    <div className="timeline-content">
                      <strong>Latency:</strong> <code>{traceMeta.latency_sec.toFixed(3)}s</code>
                    </div>
                  </div>
                  <div className="timeline-step">
                    <div className="timeline-dot" />
                    <div className="timeline-content">
                      <strong>Retries:</strong> <code>{traceMeta.retries}</code>
                    </div>
                  </div>
                  {traceMeta.failures.length > 0 && (
                    <div className="timeline-step">
                      <div className="timeline-dot timeline-dot--error" />
                      <div className="timeline-content">
                        <strong>Errors:</strong>
                        <ul className="failure-list">
                          {traceMeta.failures.map((f, i) => (
                            <li key={i}><code>{f}</code></li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </>
              )}
              <div className="timeline-step">
                <div className="timeline-dot" />
                <div className="timeline-content">
                  <strong>Finalized:</strong> Status <code>{turn.action_result.status}</code>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Retrieved Citations */}
        {turn.policy_result && (
          <div className="telemetry-section">
            <h3 className="telemetry-label">Retrieved Knowledge Citations</h3>
            {citations.length > 0 ? (
              <div className="citation-list">
                {citations.map((cit, i) => (
                  <div key={i} className="citation-item">
                    <div className="citation-title">📁 {cit.title}</div>
                    <div className="citation-meta">
                      Source: <code>{cit.source}</code> · Rank: <code>{cit.rank}</code>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-citations">No documents matched the query intent.</p>
            )}
          </div>
        )}

        {/* Graph Visualization */}
        {turn.graph_visualization && (
          <div className="telemetry-section">
            <button
              className="collapsible-header"
              onClick={() => setShowGraph(!showGraph)}
            >
              <span>🕸️ Orchestration Graph Topology</span>
              <span className="chevron">{showGraph ? "▾" : "▸"}</span>
            </button>
            {showGraph && (
              <pre className="graph-code">{turn.graph_visualization}</pre>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
