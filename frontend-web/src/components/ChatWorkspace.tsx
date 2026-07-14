import { useState, type RefObject } from "react";
import type { ChatTurn } from "../types";

interface ChatWorkspaceProps {
  chatHistory: ChatTurn[];
  loading: boolean;
  error: string | null;
  onSend: (text: string) => void;
  scrollRef: RefObject<HTMLDivElement | null>;
}

export default function ChatWorkspace({
  chatHistory,
  loading,
  error,
  onSend,
  scrollRef,
}: ChatWorkspaceProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !loading) {
        onSend(input.trim());
        setInput("");
      }
    }
  };

  return (
    <section className="chat-workspace">
      <div className="chat-header">
        <span className="chat-header-title">Workspace</span>
        {chatHistory.length > 0 && (
          <span className="chat-header-meta">
            {chatHistory.length} turn{chatHistory.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      <div className="chat-messages" ref={scrollRef}>
        {chatHistory.length === 0 && !loading && (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <div className="chat-empty-content">
              <h2 className="chat-empty-title">
                Ask anything about HR
              </h2>
              <p className="chat-empty-desc">
                Query leave balances, apply for time off, retrieve payslips, or get answers to policy questions.
              </p>
            </div>
            <div className="suggestion-grid">
              <button
                className="chip"
                onClick={() =>
                  onSend("What is my sick leave balance? My ID is EMP-999")
                }
              >
                <span className="chip-icon">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                </span>
                Check leave balance
              </button>
              <button
                className="chip"
                onClick={() => onSend("What is the notice period policy?")}
              >
                <span className="chip-icon">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                </span>
                Notice period policy
              </button>
              <button
                className="chip"
                onClick={() =>
                  onSend("Fetch my July payslip, employee ID EMP-999")
                }
              >
                <span className="chip-icon">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                </span>
                Fetch payslip
              </button>
            </div>
          </div>
        )}

        {chatHistory.map((turn, i) => (
          <div key={i} className="turn-group" style={{ animationDelay: `${i * 0.05}s` }}>
            <div className="message">
              <div className="message-avatar message-avatar--user">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
              <div className="message-body">
                <span className="message-sender">You</span>
                <div className="message-bubble message-bubble--user">
                  <p>{turn.user_input}</p>
                </div>
              </div>
            </div>

            <div className="message">
              <div className="message-avatar message-avatar--assistant">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
              </div>
              <div className="message-body">
                <span className="message-sender">Darwin</span>
                <div className="message-bubble message-bubble--assistant">
                  <p>{turn.summary}</p>

                  {turn.executed_agents.length > 0 && (
                    <div className="agent-badges">
                      {turn.executed_agents.map((a) => (
                        <span key={a} className="agent-tag">
                          {a}
                        </span>
                      ))}
                    </div>
                  )}

                  {(turn.employee_id || (turn.start_date && turn.end_date)) && (
                    <div className="memory-context">
                      {turn.employee_id && (
                        <span className="memory-badge">
                          {turn.employee_id}
                        </span>
                      )}
                      {turn.start_date && turn.end_date && (
                        <span className="memory-badge">
                          {turn.start_date} &rarr; {turn.end_date}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message" style={{ animation: "messageIn 0.2s ease both" }}>
            <div className="message-avatar message-avatar--assistant">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            </div>
            <div className="message-body">
              <span className="message-sender">Darwin</span>
              <div className="message-bubble message-bubble--assistant">
                <div className="typing-indicator">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}
      </div>

      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <div className="chat-input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question..."
            disabled={loading}
            autoFocus
          />
          <span className={`input-hint ${input.trim() ? "input-hint--hidden" : ""}`}>
            Enter &crarr;
          </span>
        </div>
        <button className="send-btn" type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
