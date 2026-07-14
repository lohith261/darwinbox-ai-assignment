import type {
  HealthResponse,
  WorkflowInvokeRequest,
  WorkflowInvokeResponse,
} from "./types";

const BASE_URL = "/api/v1";

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE_URL}/../health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function invokeWorkflow(
  payload: WorkflowInvokeRequest,
): Promise<WorkflowInvokeResponse> {
  const res = await fetch(`${BASE_URL}/workflows/invoke`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`Workflow invoke failed: ${text}`);
  }
  return res.json();
}
