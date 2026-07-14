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
  const statusColor = {
    checking: "var(--text-muted)",
    online: "var(--success)",
    offline: "var(--error)",
  }[backendStatus];

  const statusLabel = {
    checking: "Connecting",
    online: "Connected",
    offline: "Offline",
  }[backendStatus];

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
          <div>
            <h1 className="logo-title">Darwin</h1>
            <p className="logo-subtitle">HR Workflow Engine</p>
          </div>
        </div>
      </div>

      <div className="sidebar-section">
        <h2 className="section-label">Session</h2>
        <div className="session-id-box">
          <span className="session-id-label">ID</span>
          <code className="session-id-value">{sessionId.slice(0, 8)}</code>
        </div>
        <button className="reset-btn" onClick={onReset}>
          New session
        </button>
      </div>

      <div className="sidebar-section">
        <h2 className="section-label">Cost Analytics</h2>
        <div className="stat-card">
          <span className="stat-label">Naive cost</span>
          <span className="stat-value">${totalNaive.toFixed(6)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Optimized</span>
          <span className="stat-value">${totalOptimized.toFixed(6)}</span>
        </div>
        <div className="stat-card stat-card--accent">
          <span className="stat-label">Saved</span>
          <span className="stat-value">{savingsPercent.toFixed(1)}%</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Turns</span>
          <span className="stat-value">{turnCount}</span>
        </div>
      </div>

      <div className="sidebar-section">
        <h2 className="section-label">Stack</h2>
        <div className="meta-row">
          <span>Runtime</span>
          <code>Edge Function</code>
        </div>
        <div className="meta-row">
          <span>Routing</span>
          <code>Supervisor</code>
        </div>
        <div className="meta-row">
          <span>Retrieval</span>
          <code>TF-IDF</code>
        </div>
        <div className="meta-row">
          <span>Model</span>
          <code>gpt-4.1-mini</code>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="status-pill">
          <span className="status-dot" style={{ background: statusColor }} />
          {statusLabel}
        </div>
      </div>
    </aside>
  );
}
