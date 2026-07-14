interface SidebarProps {
  sessionId: string;
  onReset: () => void;
  backendStatus: "checking" | "online" | "offline";
  totalNaive: number;
  totalOptimized: number;
  savingsPercent: number;
  turnCount: number;
}

export default function Sidebar({
  sessionId,
  onReset,
  backendStatus,
  totalNaive,
  totalOptimized,
  savingsPercent,
  turnCount,
}: SidebarProps) {
  const hasActivity = turnCount > 0;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <div className="logo-mark">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <div className="logo-text">
            <h1 className="logo-title">Darwin</h1>
            <p className="logo-subtitle">HR Workflow Engine</p>
          </div>
        </div>
      </div>

      <div className="sidebar-section">
        <h2 className="section-label">Session</h2>
        <div className="session-box">
          <div className="session-row">
            <span className="session-label">Active session</span>
            <span className="session-value">{sessionId.slice(0, 8)}</span>
          </div>
        </div>
        <button className="reset-btn" onClick={onReset}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          New session
        </button>
      </div>

      {hasActivity && (
        <div className="sidebar-section">
          <h2 className="section-label">Cost Analytics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-label">Naive</span>
              <span className="stat-value">${totalNaive.toFixed(4)}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Optimized</span>
              <span className="stat-value">${totalOptimized.toFixed(4)}</span>
            </div>
            <div className="stat-card stat-card--wide stat-card--accent">
              <span className="stat-label">Cost saved</span>
              <span className="stat-value">{savingsPercent.toFixed(1)}%</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Turns</span>
              <span className="stat-value">{turnCount}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Avg/turn</span>
              <span className="stat-value">
                ${turnCount > 0 ? (totalOptimized / turnCount).toFixed(4) : "0"}
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="sidebar-section">
        <h2 className="section-label">Architecture</h2>
        <div className="meta-list">
          <div className="meta-row">
            <span>Runtime</span>
            <code>Edge Function</code>
          </div>
          <div className="meta-row">
            <span>Orchestration</span>
            <code>Supervisor</code>
          </div>
          <div className="meta-row">
            <span>Retrieval</span>
            <code>TF-IDF RAG</code>
          </div>
          <div className="meta-row">
            <span>Model</span>
            <code>gpt-4.1-mini</code>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className={`status-pill ${backendStatus === "online" ? "status-pill--online" : backendStatus === "offline" ? "status-pill--offline" : ""}`}>
          <span className={`status-dot status-dot--${backendStatus}`} />
          {backendStatus === "checking" ? "Connecting..." : backendStatus === "online" ? "System operational" : "System offline"}
        </div>
      </div>
    </aside>
  );
}
