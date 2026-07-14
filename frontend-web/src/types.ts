export interface WorkflowInvokeRequest {
  user_input: string;
  session_id?: string;
}

export interface RouteDecision {
  next_agents: string[];
  rationale: string;
}

export interface Citation {
  title: string;
  source: string;
  rank: number;
  content?: string;
}

export interface PolicyResult {
  answer: string;
  status: string;
  citations: Citation[];
}

export interface TraceMetadata {
  latency_sec: number;
  retries: number;
  failures: string[];
}

export interface ActionResult {
  tool: string;
  summary: string;
  status: string;
  output: Record<string, unknown> | null;
}

export interface WorkflowInvokeResponse {
  session_id: string;
  route_decision: RouteDecision;
  executed_agents: string[];
  messages: Array<Record<string, unknown>>;
  graph_visualization: string;
  policy_result: PolicyResult | null;
  action_result: ActionResult | null;
  employee_id: string | null;
  start_date: string | null;
  end_date: string | null;
  naive_cost: number | null;
  optimized_cost: number | null;
  percentage_reduction: number | null;
  latency_sec: number | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  environment: string;
}

export interface ChatTurn {
  user_input: string;
  summary: string;
  executed_agents: string[];
  employee_id: string | null;
  start_date: string | null;
  end_date: string | null;
  naive_cost: number;
  optimized_cost: number;
  percentage_reduction: number;
  route_decision: RouteDecision;
  policy_result: PolicyResult | null;
  action_result: ActionResult | null;
  graph_visualization: string | null;
  latency_sec: number;
  prompt_tokens: number;
  completion_tokens: number;
}
