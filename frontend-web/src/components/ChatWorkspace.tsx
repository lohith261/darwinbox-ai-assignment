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
        <h2>Workspace</h2>
      </div>

      <div className="chat-messages" ref={scrollRef}>
        {chatHistory.length === 0 && !loading && (
          <div className="chat-empty">
            <p className="chat-empty-title">What can I help with?</p>
            <p>
              Query employee leave balances, apply for time off, fetch payslips,
              or ask about HR policies.
            </p>
            <div className="suggestion-chips">
              <button
                className="chip"
                onClick={() =>
                  onSend("What is my sick leave balance? My ID is EMP-999")
                }
              >
                Check leave balance
              </button>
              <button
                className="chip"
                onClick={() => onSend("What is the notice period policy?")}
              >
                Notice period policy
              </button>
              <button
                className="chip"
                onClick={() =>
                  onSend("Fetch my July payslip, employee ID EMP-999")
                }
              >
                Fetch payslip
              </button>
            </div>
          </div>
        )}

        {chatHistory.map((turn, i) => (
          <div key={i} className="turn-group">
            <div className="message">
              <div className="message-avatar message-avatar--user">Y</div>
              <div className="message-bubble message-bubble--user">
                <p>{turn.user_input}</p>
              </div>
            </div>

            <div className="message">
              <div className="message-avatar">D</div>
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
                        {turn.start_date} to {turn.end_date}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message">
            <div className="message-avatar">D</div>
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
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>

      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
