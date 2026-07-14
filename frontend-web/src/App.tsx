import { useState, useCallback, useRef, useEffect } from "react";
import type { ChatTurn, WorkflowInvokeResponse } from "./types";
import { invokeWorkflow, checkHealth } from "./api";
import Sidebar from "./components/Sidebar";
import ChatWorkspace from "./components/ChatWorkspace";
import TelemetryPanel from "./components/TelemetryPanel";
import "./App.css";

function generateSessionId(): string {
  return crypto.randomUUID();
}

function responseToTurn(
  userInput: string,
  data: WorkflowInvokeResponse,
): ChatTurn {
  let summary = "Request processed successfully.";
  if (data.action_result?.summary) {
    summary = data.action_result.summary;
  } else if (data.policy_result?.answer) {
    summary = data.policy_result.answer;
  }

  return {
    user_input: userInput,
    summary,
    executed_agents: data.executed_agents ?? [],
    employee_id: data.employee_id,
    start_date: data.start_date,
    end_date: data.end_date,
    naive_cost: data.naive_cost ?? 0,
    optimized_cost: data.optimized_cost ?? 0,
    percentage_reduction: data.percentage_reduction ?? 0,
    route_decision: data.route_decision ?? { next_agents: [], rationale: "" },
    policy_result: data.policy_result,
    action_result: data.action_result,
    graph_visualization: data.graph_visualization ?? null,
    latency_sec: data.latency_sec ?? 0,
    prompt_tokens: data.prompt_tokens ?? 0,
    completion_tokens: data.completion_tokens ?? 0,
  };
}

export default function App() {
  const [sessionId, setSessionId] = useState(generateSessionId);
  const [chatHistory, setChatHistory] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const scrollRef = useRef<HTMLDivElement>(null);

  const totalNaive = chatHistory.reduce((s, t) => s + t.naive_cost, 0);
  const totalOptimized = chatHistory.reduce((s, t) => s + t.optimized_cost, 0);
  const savingsPercent =
    totalNaive > 0 ? ((totalNaive - totalOptimized) / totalNaive) * 100 : 0;

  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus("online"))
      .catch(() => setBackendStatus("offline"));
  }, []);

  const handleSend = useCallback(
    async (text: string) => {
      if (!text.trim() || loading) return;
      setLoading(true);
      setError(null);
      try {
        const data = await invokeWorkflow({
          user_input: text,
          session_id: sessionId,
        });
        setChatHistory((prev) => [...prev, responseToTurn(text, data)]);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to reach backend");
        setBackendStatus("offline");
      } finally {
        setLoading(false);
      }
    },
    [loading, sessionId],
  );

  const handleReset = useCallback(() => {
    setSessionId(generateSessionId());
    setChatHistory([]);
    setError(null);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory, loading]);

  const lastTurn = chatHistory.length > 0 ? chatHistory[chatHistory.length - 1] : null;

  return (
    <div className="app">
      <Sidebar
        sessionId={sessionId}
        onReset={handleReset}
        backendStatus={backendStatus}
        totalNaive={totalNaive}
        totalOptimized={totalOptimized}
        savingsPercent={savingsPercent}
        turnCount={chatHistory.length}
      />
      <main className="main-content">
        <div className="content-grid">
          <ChatWorkspace
            chatHistory={chatHistory}
            loading={loading}
            error={error}
            onSend={handleSend}
            scrollRef={scrollRef}
          />
          <TelemetryPanel turn={lastTurn} loading={loading} />
        </div>
      </main>
    </div>
  );
}
