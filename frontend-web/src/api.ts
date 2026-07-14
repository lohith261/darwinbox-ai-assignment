import type {
  HealthResponse,
  WorkflowInvokeRequest,
  WorkflowInvokeResponse,
} from "./types";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

function getBaseUrl(): string {
  if (SUPABASE_URL) {
    return `${SUPABASE_URL}/functions/v1/hr-workflow`;
  }
  return "/api/v1";
}

const BASE_URL = getBaseUrl();

const headers: Record<string, string> = {
  "Content-Type": "application/json",
  ...(SUPABASE_ANON_KEY
    ? { Authorization: `Bearer ${SUPABASE_ANON_KEY}`, Apikey: SUPABASE_ANON_KEY }
    : {}),
};

export async function checkHealth(): Promise<HealthResponse> {
  const url = SUPABASE_URL
    ? `${BASE_URL}/health`
    : `${BASE_URL}/../health`;
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function invokeWorkflow(
  payload: WorkflowInvokeRequest,
): Promise<WorkflowInvokeResponse> {
  const url = SUPABASE_URL
    ? `${BASE_URL}/invoke`
    : `${BASE_URL}/workflows/invoke`;
  const res = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`Workflow invoke failed: ${text}`);
  }
  return res.json();
}
