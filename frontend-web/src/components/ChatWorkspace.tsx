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

  return (
    <section className="chat-workspace">
      <div className="panel-header">
        <h2>Conversational Workspace</h2>
      </div>

      <div className="chat-messages" ref={scrollRef}>
        {chatHistory.length === 0 && !loading && (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>
            <p>Ask about employee leave, balances, payslips, or HR policies.</p>
            <div className="suggestion-chips">
              <button
                className="chip"
                onClick={() => onSend("What is my sick leave balance? My ID is EMP-999")}
              >
                Check sick leave balance
              </button>
              <button
                className="chip"
                onClick={() => onSend("What is the notice period policy?")}
              >
                Ask about notice period
              </button>
              <button
                className="chip"
                onClick={() => onSend("Fetch my July payslip, employee ID EMP-999")}
              >
                Fetch payslip
              </button>
            </div>
          </div>
        )}

        {chatHistory.map((turn, i) => (
          <div key={i} className="turn-group">
            <div className="message message-user">
              <div className="message-avatar">👤</div>
              <div className="message-bubble message-bubble--user">
                <p>{turn.user_input}</p>
              </div>
            </div>

            <div className="message message-assistant">
              <div className="message-avatar">🧬</div>
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

                <div className="memory-context">
                  {turn.employee_id && (
                    <span className="memory-badge">🧠 Employee: {turn.employee_id}</span>
                  )}
                  {turn.start_date && turn.end_date && (
                    <span className="memory-badge">
                      🧠 Dates: {turn.start_date} → {turn.end_date}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message message-assistant">
            <div className="message-avatar">🧬</div>
            <div className="message-bubble message-bubble--assistant">
              <div className="typing-indicator">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="error-banner">
            <strong>Connection error:</strong> {error}
          </div>
        )}
      </div>

      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Query employee leave, balances, or payslips…"
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Sending…" : "Send"}
        </button>
      </form>
    </section>
  );
}
