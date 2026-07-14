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
        <div className="telemetry-header">
          <span className="telemetry-header-title">Telemetry</span>
        </div>
        <div className="telemetry-empty">
          <div className="telemetry-empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </div>
          <p>Run a query to see agent traces, routing decisions, and cost metrics here.</p>
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
      <div className="telemetry-header">
        <span className="telemetry-header-title">Telemetry</span>
        <span className="telemetry-header-badge">
          {turn.latency_sec.toFixed(1)}s
        </span>
      </div>

      <div className="telemetry-scroll">
        <div className="telemetry-section">
          <h3 className="telemetry-label">Agent Status</h3>
          <div className="status-grid">
            <div
              className={`status-card ${policyActive ? (policyStatus === "grounded" ? "status--success" : "status--error") : "status--idle"}`}
            >
              <div className="status-icon">
                {policyActive
                  ? policyStatus === "grounded"
                    ? "\u2713"
                    : "\u2717"
                  : "\u2014"}
              </div>
              <div className="status-info">
                <div className="status-name">Policy</div>
                <div className="status-detail">
                  {!policyActive
                    ? "Idle"
                    : policyStatus === "grounded"
                      ? "Grounded"
                      : "Not found"}
                </div>
              </div>
            </div>

            <div
              className={`status-card ${actionActive ? (actionStatus === "success" || actionStatus === "approved" ? "status--success" : "status--error") : "status--idle"}`}
            >
              <div className="status-icon">
                {actionActive
                  ? actionStatus === "success" || actionStatus === "approved"
                    ? "\u2713"
                    : "\u2717"
                  : "\u2014"}
              </div>
              <div className="status-info">
                <div className="status-name">Action</div>
                <div className="status-detail">
                  {!actionActive
                    ? "Idle"
                    : actionStatus === "success" || actionStatus === "approved"
                      ? "Success"
                      : "Failed"}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="telemetry-section">
          <h3 className="telemetry-label">Performance</h3>
          <div className="metric-grid">
            <div className="metric-box">
              <span className="metric-label">Latency</span>
              <span className="metric-value">
                {turn.latency_sec >= 1
                  ? `${turn.latency_sec.toFixed(2)}s`
                  : `${(turn.latency_sec * 1000).toFixed(0)}ms`}
              </span>
            </div>
            <div className="metric-box">
              <span className="metric-label">Cost saved</span>
              <span className="metric-value">
                {turn.percentage_reduction.toFixed(0)}%
              </span>
            </div>
          </div>
          <div className="token-row">
            <span>
              Prompt <code>{turn.prompt_tokens}</code>
            </span>
            <span>
              Completion <code>{turn.completion_tokens}</code>
            </span>
          </div>
        </div>

        <div className="telemetry-section">
          <h3 className="telemetry-label">Routing Decision</h3>
          <div className="route-badge-wrapper">
            {isBypass ? (
              <span className="route-badge route-badge--bypass">Deterministic bypass</span>
            ) : (
              <span className="route-badge route-badge--llm">LLM routed</span>
            )}
          </div>
          <p className="rationale">{turn.route_decision.rationale}</p>
          <div className="orchestration-path">
            <span className="path-node">START</span>
            <span className="path-arrow">&rarr;</span>
            {turn.executed_agents.map((a, i) => (
              <span key={a}>
                <span className="path-node">{a}</span>
                {i < turn.executed_agents.length - 1 && (
                  <span className="path-arrow">&rarr;</span>
                )}
              </span>
            ))}
            <span className="path-arrow">&rarr;</span>
            <span className="path-node">END</span>
          </div>
        </div>

        {turn.action_result && turn.action_result.tool && (
          <div className="telemetry-section">
            <h3 className="telemetry-label">Tool Execution</h3>
            <div className="timeline">
              <div className="timeline-step">
                <div className="timeline-dot" />
                <div className="timeline-content">
                  <strong>Invoke</strong> <code>action_agent</code>
                </div>
              </div>
              <div className="timeline-step">
                <div className="timeline-dot" />
                <div className="timeline-content">
                  <strong>Execute</strong> <code>{turn.action_result.tool}</code>
                </div>
              </div>
              {traceMeta && (
                <>
                  <div className="timeline-step">
                    <div className="timeline-dot" />
                    <div className="timeline-content">
                      <strong>Duration</strong>{" "}
                      <code>{traceMeta.latency_sec.toFixed(3)}s</code>
                      {traceMeta.retries > 0 && (
                        <> with <code>{traceMeta.retries}</code> retries</>
                      )}
                    </div>
                  </div>
                  {traceMeta.failures.length > 0 && (
                    <div className="timeline-step">
                      <div className="timeline-dot timeline-dot--error" />
                      <div className="timeline-content">
                        <strong>Failures</strong>
                        <ul className="failure-list">
                          {traceMeta.failures.map((f, i) => (
                            <li key={i}>
                              <code>{f}</code>
                            </li>
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
                  <strong>Complete</strong>{" "}
                  <code>{turn.action_result.status}</code>
                </div>
              </div>
            </div>
          </div>
        )}

        {turn.policy_result && citations.length > 0 && (
          <div className="telemetry-section">
            <h3 className="telemetry-label">
              Sources ({citations.length})
            </h3>
            <div className="citation-list">
              {citations.map((cit, i) => (
                <div key={i} className="citation-item">
                  <div className="citation-title">{cit.title}</div>
                  <div className="citation-meta">
                    <code>{cit.source}</code> &middot; Rank {cit.rank}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {turn.graph_visualization && (
          <div className="telemetry-section">
            <button
              className="collapsible-header"
              onClick={() => setShowGraph(!showGraph)}
            >
              <span>Graph topology</span>
              <span className={`chevron ${showGraph ? "chevron--open" : ""}`}>&#9654;</span>
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
