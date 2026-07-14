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
  const statusInfo = {
    checking: { label: "Checking…", color: "var(--accent)" },
    online: { label: "Online", color: "var(--success)" },
    offline: { label: "Offline", color: "var(--error)" },
  }[backendStatus];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">🧬</span>
          <div>
            <h1 className="logo-title">Darwin</h1>
            <p className="logo-subtitle">HR Observability Engine</p>
          </div>
        </div>
      </div>

      <div className="sidebar-section">
        <h2 className="section-label">Session Controls</h2>
        <div className="session-id-box">
          <span className="session-id-label">Active Session</span>
          <code className="session-id-value">{sessionId.slice(0, 8)}…</code>
        </div>
        <button className="reset-btn" onClick={onReset}>
          Reset Session & Telemetry
        </button>
      </div>

      <div className="sidebar-section">
        <h2 className="section-label">Session Statistics</h2>
        <div className="stat-card">
          <span className="stat-label">Total Naive Cost</span>
          <span className="stat-value">${totalNaive.toFixed(6)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total Optimized Cost</span>
          <span className="stat-value">${totalOptimized.toFixed(6)}</span>
        </div>
        <div className="stat-card stat-card--accent">
          <span className="stat-label">Token Savings</span>
          <span className="stat-value">{savingsPercent.toFixed(1)}%</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total Turns</span>
          <span className="stat-value">{turnCount}</span>
        </div>
      </div>

      <div className="sidebar-section">
        <h2 className="section-label">System Metadata</h2>
        <div className="meta-row">
          <span>Environment</span>
          <code>LOCAL</code>
        </div>
        <div className="meta-row">
          <span>API Gateway</span>
          <code>localhost:8000</code>
        </div>
        <div className="meta-row">
          <span>Vector Store</span>
          <code>ChromaDB</code>
        </div>
        <div className="meta-row">
          <span>Model</span>
          <code>gpt-4.1-mini</code>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="status-pill" style={{ borderColor: statusInfo.color }}>
          <span className="status-dot" style={{ background: statusInfo.color }} />
          Backend {statusInfo.label}
        </div>
      </div>
    </aside>
  );
}
