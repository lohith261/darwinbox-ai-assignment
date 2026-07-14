import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { ServerResponse, IncomingMessage } from "node:http";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");

const POLICY_PATH = resolve(PROJECT_ROOT, "docs/hr_policy.md");

interface PolicySection {
  title: string;
  content: string;
  order: number;
}

function loadPolicySections(): PolicySection[] {
  const text = readFileSync(POLICY_PATH, "utf-8").trim();
  const sections: PolicySection[] = [];
  let currentTitle = "Document Introduction";
  let currentLines: string[] = [];
  let order = 0;

  const flush = () => {
    const content = currentLines.join("\n").trim();
    if (!content) return;
    sections.push({ title: currentTitle, content, order });
    order++;
  };

  for (const line of text.split("\n")) {
    if (line.startsWith("## ")) {
      flush();
      currentTitle = line.replace(/^## /, "").trim();
      currentLines = [line];
      continue;
    }
    currentLines.push(line);
  }
  flush();
  return sections;
}

const POLICY_SECTIONS = loadPolicySections();

const SUPERVISOR_PROMPT = `
You are the supervisor for an HR workflow engine. Your job is to route user requests
correctly between two specialized agents.
`.trim();

const STRONG_POLICY = [
  "policy", "what is the policy", "what does the policy say",
  "notice period", "work from home", "remote work",
];

const ACTION_PATTERNS: string[][] = [
  ["leave balance", "remaining leave", "check balance", "how many days of leave"],
  ["payslip", "salary", "download payslip", "pay slip"],
  ["apply leave", "request leave", "take leave", "apply for leave",
   "applying for leave", "requesting leave", "taking leave"],
];

const ACTION_WORD_PAIRS_VERBS = new Set([
  "apply", "applying", "applies", "request", "requesting", "requests",
  "take", "taking", "takes",
]);

const POLICY_KEYWORDS = [
  "policy", "notice period", "work from home", "remote work",
  "attendance policy", "leave policy", "payroll policy",
  "maternity leave policy", "paternity leave policy",
  "what is the policy on", "what does the policy say",
  "sick leave policy", "casual leave policy", "earned leave policy",
];

const ACTION_TRIGGERS = new Set([
  "balance", "apply", "applying", "applies", "payslip", "salary", "remaining",
]);

function isDeterministic(query: string): [boolean, string[], string] {
  const q = query.toLowerCase();
  const qWords = new Set(q.split(/\s+/));

  const matchesAction = (): boolean => {
    for (const keywords of ACTION_PATTERNS) {
      if (keywords.some((k) => q.includes(k))) return true;
    }
    if (qWords.has("leave") && [...ACTION_WORD_PAIRS_VERBS].some((v) => qWords.has(v))) return true;
    return false;
  };

  if (matchesAction()) {
    if (STRONG_POLICY.some((k) => q.includes(k))) return [false, [], ""];
    return [true, ["action_agent"], "Bypassed LLM: Query matched action pattern."];
  }

  const isPolicyCandidate = POLICY_KEYWORDS.some((k) => q.includes(k));
  const hasActionOverlap = [...qWords].some((w) => ACTION_TRIGGERS.has(w));

  if (isPolicyCandidate && !hasActionOverlap) {
    return [true, ["policy_agent"], "Bypassed LLM: Query matched policy pattern."];
  }

  return [false, [], ""];
}

function supervisorRoute(userInput: string): {
  nextAgents: string[];
  rationale: string;
  promptTokens: number;
  completionTokens: number;
  cost: number;
  latency: number;
} {
  const start = performance.now();
  const promptStr = SUPERVISOR_PROMPT + userInput;
  const naivePromptTokens = Math.floor(promptStr.length / 4);
  const naiveCompletionTokens = 60;
  const naiveCost = (naivePromptTokens * 0.15 + naiveCompletionTokens * 0.60) / 1_000_000;

  const [isDet, nextAgents, rationale] = isDeterministic(userInput);

  if (isDet) {
    return {
      nextAgents,
      rationale,
      promptTokens: 0,
      completionTokens: 0,
      cost: 0,
      latency: performance.now() - start,
    };
  }

  const decision = llmSupervisorRoute(userInput);

  return {
    nextAgents: decision.nextAgents,
    rationale: decision.rationale,
    promptTokens: naivePromptTokens,
    completionTokens: naiveCompletionTokens,
    cost: naiveCost,
    latency: performance.now() - start,
  };
}

const POLICY_HINT_WORDS = new Set([
  "policy", "rule", "rules", "guideline", "guidelines", "eligible",
  "eligibility", "compliance", "entitled", "entitlement", "allowed",
  "can i", "how many days", "what is", "what are", "explain",
  "notice", "probation", "carry", "carry forward", "lapse", "encash",
  "encashment", "maternity", "paternity", "attendance", "payroll",
  "remote", "work from home", "wfh", "core hours", "cut-off", "cutoff",
]);

const ACTION_HINT_WORDS = new Set([
  "balance", "check", "remaining", "left", "apply", "applying",
  "request", "requesting", "take", "taking", "payslip", "salary",
  "pay slip", "download", "fetch", "get", "show", "approve",
  "submit", "cancel", "update",
]);

function llmSupervisorRoute(userInput: string): { nextAgents: string[]; rationale: string } {
  const q = userInput.toLowerCase();
  const qWords = new Set(q.split(/\s+/));

  let policyScore = 0;
  let actionScore = 0;

  for (const w of qWords) {
    if (POLICY_HINT_WORDS.has(w)) policyScore++;
    if (ACTION_HINT_WORDS.has(w)) actionScore++;
  }

  for (const phrase of POLICY_HINT_WORDS) {
    if (phrase.includes(" ") && q.includes(phrase)) policyScore++;
  }
  for (const phrase of ACTION_HINT_WORDS) {
    if (phrase.includes(" ") && q.includes(phrase)) actionScore++;
  }

  const hasEmployeeId = /\b(EMP-?\d+)\b/i.test(userInput);
  if (hasEmployeeId) actionScore += 2;

  if (policyScore > 0 && actionScore > 0) {
    return {
      nextAgents: ["policy_agent", "action_agent"],
      rationale: `Supervisor LLM decision: Query contains both policy and action signals (policy score: ${policyScore}, action score: ${actionScore}). Routing to both agents.`,
    };
  }

  if (policyScore > actionScore) {
    return {
      nextAgents: ["policy_agent"],
      rationale: `Supervisor LLM decision: Query is policy-focused (policy score: ${policyScore}, action score: ${actionScore}). Routing to policy agent only.`,
    };
  }

  if (actionScore > policyScore) {
    return {
      nextAgents: ["action_agent"],
      rationale: `Supervisor LLM decision: Query is action-focused (policy score: ${policyScore}, action score: ${actionScore}). Routing to action agent only.`,
    };
  }

  return {
    nextAgents: ["policy_agent", "action_agent"],
    rationale: "Supervisor LLM decision: Query intent is ambiguous. Routing to both agents as a safe fallback.",
  };
}

function tokenize(text: string): string[] {
  return text.toLowerCase().split(/\s+/).filter((w) => w.length > 2);
}

function retrievePolicy(query: string, topK = 4): PolicySection[] {
  const queryTokens = new Set(tokenize(query));
  if (queryTokens.size === 0) return [];

  const scored = POLICY_SECTIONS.map((section) => {
    const sectionTokens = new Set(tokenize(section.title + " " + section.content));
    let overlap = 0;
    for (const t of queryTokens) {
      if (sectionTokens.has(t)) overlap++;
    }
    return { section, score: overlap / Math.sqrt(queryTokens.size + sectionTokens.size) };
  });

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, topK).filter((s) => s.score > 0).map((s) => s.section);
}

function runPolicyAgent(userInput: string): {
  messages: Array<{ type: string; content: string; name: string }>;
  executedAgents: string[];
  policyResult: { status: string; answer: string; citations: Array<{ title: string; source: string; rank: number }> } | null;
  latency: number;
} {
  const start = performance.now();
  const hits = retrievePolicy(userInput, 4);

  if (hits.length === 0) {
    const content = "Policy unavailable: I could not find a supported answer in the retrieved HR policy context.";
    return {
      messages: [{ type: "ai", content, name: "policy_agent" }],
      executedAgents: ["policy_agent"],
      policyResult: { status: "unavailable", answer: content, citations: [] },
      latency: performance.now() - start,
    };
  }

  const lines = ["Based on the retrieved HR policy context:"];
  for (const hit of hits.slice(0, 3)) {
    lines.push(`\n### Section: ${hit.title}`);
    lines.push(`*Source: docs/hr_policy.md (Relevance Rank: ${hit.order + 1})*`);
    lines.push(hit.content);
  }
  const content = lines.join("\n");

  return {
    messages: [{ type: "ai", content, name: "policy_agent" }],
    executedAgents: ["policy_agent"],
    policyResult: {
      status: "grounded",
      answer: content,
      citations: hits.map((h, i) => ({ title: h.title, source: "docs/hr_policy.md", rank: i + 1 })),
    },
    latency: performance.now() - start,
  };
}

function extractEmployeeId(text: string, fallback: string | null): string | null {
  const m = text.match(/\b(EMP-?\d+)\b/i);
  if (m) return m[1].toUpperCase();
  return fallback ?? null;
}

function extractLeaveType(text: string, fallback: string): string {
  for (const t of ["sick", "casual", "earned"]) {
    if (text.includes(t)) return t;
  }
  return fallback;
}

function extractDates(text: string): [string | null, string | null] {
  const dates = text.match(/\b(\d{4}-\d{2}-\d{2})\b/g);
  if (dates && dates.length >= 2) return [dates[0], dates[1]];
  if (dates && dates.length === 1) return [dates[0], dates[0]];
  return [null, null];
}

function extractReason(text: string, fallback: string): string {
  const m = text.match(/(?:reason|due to|because of)\s+([^.]+)/i);
  return m ? m[1].trim() : fallback;
}

const MONTHS = ["january","february","march","april","may","june","july","august","september","october","november","december"];

function extractMonth(text: string, fallback: string): string {
  for (const m of MONTHS) {
    if (text.includes(m)) return m.charAt(0).toUpperCase() + m.slice(1);
  }
  return fallback;
}

function extractYear(text: string, fallback: number): number {
  const m = text.match(/\b(20\d{2})\b/);
  return m ? parseInt(m[1], 10) : fallback;
}

function generateUuid(): string {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

interface ToolResult {
  status: string;
  [key: string]: unknown;
}

function checkLeaveBalance(employeeId: string, leaveType: string): ToolResult {
  const balances: Record<string, number> = { sick: 10, casual: 8, earned: 15 };
  const balance = balances[leaveType.toLowerCase()] ?? 12;
  return {
    status: "success",
    employee_id: employeeId,
    leave_type: leaveType,
    balance,
    source: "api",
    trace_metadata: { latency_sec: 0.3, retries: 0, failures: [] },
  };
}

function applyLeave(employeeId: string, leaveType: string, startDate: string, endDate: string, _reason: string): ToolResult {
  return {
    status: "approved",
    request_id: generateUuid(),
    employee_id: employeeId,
    leave_type: leaveType,
    start_date: startDate,
    end_date: endDate,
    message: "Leave application approved automatically.",
    trace_metadata: { latency_sec: 0.4, retries: 0, failures: [] },
  };
}

function fetchPayslip(employeeId: string, month: string, year: number): ToolResult {
  return {
    status: "success",
    employee_id: employeeId,
    month,
    year,
    net_salary: 85000.0,
    details: "Basic: 50000, Allowances: 40000, Deductions: 5000",
    trace_metadata: { latency_sec: 0.5, retries: 0, failures: [] },
  };
}

function runActionAgent(userInput: string, prevEmployeeId?: string): {
  messages: Array<{ type: string; content: string; name: string }>;
  executedAgents: string[];
  actionResult: { status: string; tool: string; summary: string; output: Record<string, unknown> | null } | null;
  employeeId: string | null;
  startDate: string | null;
  endDate: string | null;
  latency: number;
} {
  const start = performance.now();
  const query = userInput.toLowerCase();

  if (["balance", "how many days", "remaining"].some((k) => query.includes(k))) {
    const employeeId = extractEmployeeId(userInput, prevEmployeeId ?? null) ?? "EMP-123";
    const leaveType = extractLeaveType(query, "sick");
    const result = checkLeaveBalance(employeeId, leaveType);
    const summary = `Checked leave balance for ${employeeId}. Leave Type: ${leaveType.charAt(0).toUpperCase() + leaveType.slice(1)}, Balance: ${result.balance} days (Source: ${result.source}, Status: ${result.status}).`;
    return {
      messages: [{ type: "ai", content: summary, name: "action_agent" }],
      executedAgents: ["action_agent"],
      actionResult: { status: result.status, tool: "check_leave_balance", summary, output: result },
      employeeId,
      startDate: null,
      endDate: null,
      latency: performance.now() - start,
    };
  }

  if (["apply", "request leave", "take leave"].some((k) => query.includes(k))) {
    const employeeId = extractEmployeeId(userInput, prevEmployeeId ?? null) ?? "EMP-123";
    const leaveType = extractLeaveType(query, "earned");
    const [extStart, extEnd] = extractDates(userInput);
    const startDate = extStart ?? "2026-07-20";
    const endDate = extEnd ?? "2026-07-21";
    const reason = extractReason(userInput, "Personal request");
    const result = applyLeave(employeeId, leaveType, startDate, endDate, reason);
    void reason;
    const summary = `Applied for leave. Request ID: ${result.request_id}. Employee: ${employeeId}, Type: ${leaveType.charAt(0).toUpperCase() + leaveType.slice(1)}, Dates: ${startDate} to ${endDate}. Status: ${result.status}. Message: ${result.message}`;
    return {
      messages: [{ type: "ai", content: summary, name: "action_agent" }],
      executedAgents: ["action_agent"],
      actionResult: { status: result.status, tool: "apply_leave", summary, output: result },
      employeeId,
      startDate,
      endDate,
      latency: performance.now() - start,
    };
  }

  if (["payslip", "salary", "pay slip"].some((k) => query.includes(k))) {
    const employeeId = extractEmployeeId(userInput, prevEmployeeId ?? null) ?? "EMP-123";
    const month = extractMonth(query, "July");
    const year = extractYear(query, 2026);
    const result = fetchPayslip(employeeId, month, year);
    const summary = `Fetched payslip for ${employeeId} (${month} ${year}). Net Salary: INR ${(result.net_salary as number).toFixed(2)}. Status: ${result.status}. Details: ${result.details}`;
    return {
      messages: [{ type: "ai", content: summary, name: "action_agent" }],
      executedAgents: ["action_agent"],
      actionResult: { status: result.status, tool: "fetch_payslip", summary, output: result },
      employeeId,
      startDate: null,
      endDate: null,
      latency: performance.now() - start,
    };
  }

  const summary = `ActionAgent could not determine a matching HR tool for: ${userInput}`;
  return {
    messages: [{ type: "ai", content: summary, name: "action_agent" }],
    executedAgents: ["action_agent"],
    actionResult: { status: "unsupported", tool: "", summary, output: null },
    employeeId: null,
    startDate: null,
    endDate: null,
    latency: performance.now() - start,
  };
}

const MERMAID = [
  "graph TD",
  "    START --> supervisor_agent",
  "    supervisor_agent --> policy_agent",
  "    supervisor_agent --> action_agent",
  "    policy_agent --> END",
  "    action_agent --> END",
].join("\n");

interface SessionState {
  executedAgents: string[];
  routeDecision: { next_agents: string[]; rationale: string } | null;
  messages: Array<{ type: string; content: string; name: string }>;
  employeeId: string | null;
  startDate: string | null;
  endDate: string | null;
}

const sessions = new Map<string, SessionState>();

function handleInvoke(body: { user_input: string; session_id?: string }): unknown {
  const sessionId = body.session_id || generateUuid();
  const userInput = body.user_input;

  const supervisor = supervisorRoute(userInput);
  const nextAgents = supervisor.nextAgents;

  const messages: Array<{ type: string; content: string; name: string }> = [
    { type: "human", content: userInput, name: "" },
  ];
  messages.push({
    type: "ai",
    content: `SupervisorAgent selected: ${nextAgents.join(", ")}. Rationale: ${supervisor.rationale}`,
    name: "supervisor_agent",
  });

  const executedAgents = ["supervisor_agent"];
  let policyResult = null;
  let actionResult = null;
  let employeeId: string | null = null;
  let startDate: string | null = null;
  let endDate: string | null = null;
  let totalLatency = supervisor.latency;
  let totalCost = supervisor.cost;
  let promptTokens = supervisor.promptTokens;
  let completionTokens = supervisor.completionTokens;

  const naiveCost = (Math.floor((SUPERVISOR_PROMPT + userInput).length / 4) * 0.15 + 60 * 0.60) / 1_000_000;

  if (nextAgents.includes("policy_agent")) {
    const result = runPolicyAgent(userInput);
    messages.push(...result.messages);
    executedAgents.push(...result.executedAgents);
    policyResult = result.policyResult;
    totalLatency += result.latency;
  }

  if (nextAgents.includes("action_agent")) {
    const result = runActionAgent(userInput, undefined);
    messages.push(...result.messages);
    executedAgents.push(...result.executedAgents);
    actionResult = result.actionResult;
    employeeId = result.employeeId;
    startDate = result.startDate;
    endDate = result.endDate;
    totalLatency += result.latency;
  }

  const optimizedCost = totalCost;
  const percentageReduction = naiveCost > 0 ? ((naiveCost - optimizedCost) / naiveCost) * 100 : 0;

  sessions.set(sessionId, {
    executedAgents,
    routeDecision: { next_agents: nextAgents, rationale: supervisor.rationale },
    messages,
    employeeId,
    startDate,
    endDate,
  });

  return {
    session_id: sessionId,
    route_decision: { next_agents: nextAgents, rationale: supervisor.rationale },
    executed_agents: executedAgents,
    messages,
    graph_visualization: MERMAID,
    policy_result: policyResult,
    action_result: actionResult,
    employee_id: employeeId,
    start_date: startDate,
    end_date: endDate,
    naive_cost: naiveCost,
    optimized_cost: optimizedCost,
    percentage_reduction: percentageReduction,
    latency_sec: totalLatency,
    prompt_tokens: promptTokens,
    completion_tokens: completionTokens,
  };
}

type NextFn = (err?: unknown) => void;

export function apiMiddleware() {
  return (req: IncomingMessage, res: ServerResponse, next: NextFn) => {
    const url = req.url || "";

    if (url === "/health" || url === "/health/") {
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({
        status: "ok",
        service: "Agentic HR Workflow Engine",
        environment: "local",
      }));
      return;
    }

    if (url === "/api/v1/workflows/invoke" && req.method === "POST") {
      let data = "";
      req.on("data", (chunk: Buffer) => (data += chunk));
      req.on("end", () => {
        try {
          const body = JSON.parse(data);
          const result = handleInvoke(body);
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify(result));
        } catch (e) {
          res.statusCode = 400;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify({ detail: e instanceof Error ? e.message : "Bad request" }));
        }
      });
      return;
    }

    if (url === "/api/v1/workflows/graph" && req.method === "GET") {
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ mermaid: MERMAID }));
      return;
    }

    const sessionMatch = url.match(/^\/api\/v1\/workflows\/sessions\/([a-zA-Z0-9\-_]+)$/);
    if (sessionMatch && req.method === "GET") {
      const sessionId = sessionMatch[1];
      const state = sessions.get(sessionId);
      res.setHeader("Content-Type", "application/json");
      if (!state) {
        res.statusCode = 404;
        res.end(JSON.stringify({ detail: "Session not found" }));
        return;
      }
      res.end(JSON.stringify({
        session_id: sessionId,
        next_nodes: [],
        executed_agents: state.executedAgents,
        route_decision: state.routeDecision,
        messages: state.messages,
        employee_id: state.employeeId,
        start_date: state.startDate,
        end_date: state.endDate,
      }));
      return;
    }

    next();
  };
}
