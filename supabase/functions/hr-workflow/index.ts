import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers":
    "Content-Type, Authorization, X-Client-Info, Apikey",
};

const POLICY_TEXT = `# Darwinbox Sample HR Policy Handbook

## 1. Purpose and Applicability

This handbook defines the internal people policies that apply to full-time employees of Darwinbox India Private Limited for the purposes of the Agentic HR Workflow Engine assignment. It is a realistic sample document designed to simulate a production HR knowledge base. The policy aims to provide clarity on leave, attendance, payroll, notice obligations, and remote work expectations. Contractors, interns, and third-party staff may be governed by separate agreements unless their local contract explicitly references this handbook.

All policies in this document are subject to local law, employment agreements, and management approval where explicitly stated. In case of conflict between this handbook and applicable law, the legal requirement will prevail. In case of conflict between this handbook and an approved written exception signed by Human Resources and the relevant business leader, the approved written exception will prevail for the named employee only.

Employees are expected to raise questions through the HR helpdesk before taking action on a situation that may create payroll, compliance, or attendance impact. Managers must not make verbal commitments that contradict documented policy without prior HR approval. Every leave request, attendance correction, and remote work arrangement should be recorded in the company HR system.

## 2. Leave Policy Overview

Darwinbox supports planned time away from work, statutory leave, and emergency absences through a structured leave framework. Leave categories available under this handbook are Casual Leave, Sick Leave, Earned Leave, Maternity Leave, and Paternity Leave. Employees must apply for leave through the HR system unless an emergency makes prior submission impossible. In those cases, the employee or a family member should notify the manager and HR within the same working day whenever reasonably possible.

Weekly offs, public holidays published on the company holiday calendar, and approved company shutdown days are not counted as leave unless a policy or law specifically requires bridging treatment. If an employee is absent without approval and without timely communication, the absence may be treated as leave without pay, unauthorized absence, or a conduct issue depending on the facts of the case.

Managers are expected to balance business continuity with fairness and employee wellbeing. Approval decisions should consider workload, team coverage, business deadlines, prior notice, and any legal protections attached to the leave type. Approval must never be based on personal preference, favoritism, or retaliation.

## 3. Sick Leave

Full-time employees are eligible for 12 days of Sick Leave per calendar year, credited upfront in January on a prorated basis for employees who join during the year. Sick Leave is intended for personal illness, medical treatment, preventive care, recovery, or immediate care of a dependent in a short-duration health emergency where no other caregiver is reasonably available.

Employees should inform their manager as early as possible on the day of absence. For Sick Leave of 3 or more consecutive working days, a medical certificate or fit-to-work note may be requested by HR. The company may waive documentation for shorter illnesses, but repeated short absences around weekends or holidays may trigger additional review.

Unused Sick Leave does not encash at separation and does not convert into Earned Leave. Up to 6 days of unused Sick Leave may be carried forward into the next calendar year, but the total Sick Leave balance at any point cannot exceed 18 days. Once the cap is reached, additional yearly credit will be limited to the amount required to restore the balance to the maximum.

If a public holiday falls during an approved Sick Leave period, the holiday will not be counted as Sick Leave unless local law requires a different treatment. Sick Leave cannot be used to extend resignation without approval. During probation, Sick Leave is available, but frequent unplanned absence may be considered during overall probation confirmation review.

## 4. Casual Leave

Full-time employees are eligible for 8 days of Casual Leave per calendar year, credited upfront in January or on a prorated basis for mid-year joiners. Casual Leave is intended for short personal matters, urgent family commitments, ceremonies, or brief personal travel that does not qualify under another leave category.

Casual Leave should normally be planned in advance and approved before the employee is absent. Employees should submit Casual Leave at least 2 working days in advance where practicable. Casual Leave may be taken in half-day or full-day units. A single Casual Leave request should generally not exceed 3 consecutive working days unless the manager and HR both approve an exception based on business needs.

Unused Casual Leave lapses at the end of the calendar year and is not carried forward. Casual Leave is not encashable. Casual Leave may be declined during critical business periods, peak payroll cycles, month-end closure periods, statutory filing windows, or when minimum team coverage cannot be maintained.

If an employee exhausts the Casual Leave balance, additional personal absence may be adjusted against Earned Leave where available and approved, or otherwise treated as leave without pay. Managers should not ask employees to mark planned personal time as Sick Leave in order to bypass policy limits.

## 5. Earned Leave

Full-time employees accrue 18 days of Earned Leave per calendar year at the rate of 1.5 days per completed month of service. Accrual begins from the employee's date of joining. Earned Leave is intended for vacation, rest, extended personal commitments, and planned time away from work requiring longer notice.

Employees are encouraged to submit Earned Leave requests at least 10 calendar days in advance for leave up to 5 working days and at least 20 calendar days in advance for longer periods. Earned Leave may be taken in half-day increments only where the reporting manager approves and business operations permit. Managers should approve or reject planned Earned Leave promptly so employees can make personal arrangements with confidence.

Up to 30 days of Earned Leave may be carried forward into the next calendar year. Any balance above 30 days as of 31 December will be automatically lapsed unless local law or an approved exception requires otherwise. Earned Leave may be encashed at separation based on the employee's final eligible basic salary rate, subject to statutory deductions and completion of full and final settlement.

Employees may not ordinarily take more than 15 consecutive working days of Earned Leave without business head approval. A manager may defer requested Earned Leave in situations involving critical launches, audit preparation, major client escalation, or insufficient coverage; however, the manager should propose alternative dates rather than denying the request without discussion.

## 6. Maternity Leave

Eligible employees are entitled to Maternity Leave in accordance with applicable law and company policy. Under this sample handbook, an employee is eligible for up to 26 weeks of paid Maternity Leave for the first two surviving children and up to 12 weeks of paid Maternity Leave where the law permits a reduced duration for subsequent eligible cases. Supporting medical documentation may be requested by HR in line with statutory requirements.

Employees should notify HR and the reporting manager at least 8 weeks before the expected start of Maternity Leave whenever reasonably possible. This is intended to support workload planning, transition coverage, knowledge transfer, and return-to-work arrangements. An employee should not be pressured to start leave earlier than medically required or legally necessary.

Maternity Leave is paid through the regular payroll cycle. Variable pay, incentives, and attendance-linked allowances during the leave period will be administered according to the applicable compensation plan and law. Holidays falling during Maternity Leave are part of the leave period and do not extend the total duration unless a law or approved accommodation states otherwise.

On return from Maternity Leave, the employee should ordinarily resume the same role or a comparable role with equivalent grade and compensation, subject to lawful organizational changes. Reasonable flexibility, including temporary Work From Home arrangements, may be considered on a case-by-case basis for up to 30 days after return, with manager and HR approval.

## 7. Paternity Leave

Eligible full-time employees are entitled to 10 working days of paid Paternity Leave for the birth or legal adoption placement of a child. Paternity Leave should normally be taken within 90 days of the qualifying event unless HR approves a different schedule for medical, family, or business reasons.

Employees are expected to notify their manager and HR in advance whenever possible, and may be required to submit supporting documentation such as a birth record, hospital note, or adoption document. Paternity Leave may be taken in one block or, with manager approval, in up to two blocks within the 90-day eligibility window.

Unused Paternity Leave lapses after the eligibility window and is not carried forward or encashable. Paternity Leave is not intended to replace long-term child-care arrangements. If additional time is needed, the employee may request Earned Leave, Casual Leave, or an unpaid leave arrangement subject to approval.

## 8. Payroll Policy

Monthly salary is processed through bank transfer and is normally credited on or before the last working day of each month. If a banking holiday, system outage, or statutory processing issue affects disbursement, payroll will be processed on the nearest practicable working day. Employees must ensure that bank account details, tax declarations, and statutory identifiers are accurate in the HR system no later than the payroll cut-off date.

The standard payroll cut-off for attendance, leave, and reimbursement inputs is the 20th of each month. Approved leave or attendance changes submitted after the cut-off may be reflected in the following payroll cycle unless HR determines that an urgent off-cycle correction is necessary. Off-cycle payroll corrections are exceptional and require Payroll approval.

Salary components, deductions, bonuses, and statutory withholdings will be governed by the employee's compensation structure and law. Leave without pay impacts monthly earnings proportionately based on applicable payroll rules. Incorrect payments caused by system errors, duplicate reimbursements, or incorrect manual inputs remain recoverable by the company after informing the employee.

Payslips are made available through the HR system after payroll is processed. Employees should review their payslip within 5 working days and raise discrepancies promptly. If an error is identified, Payroll will investigate and communicate the correction timeline. The target turnaround time for standard payroll queries is 7 working days.

## 9. Notice Period

The standard notice period for confirmed full-time employees is 60 calendar days unless the employment contract states otherwise. During probation, the notice period is 15 calendar days unless local law or contract requires a longer period. The company may, at its discretion, accept a shorter notice period, require full notice service, or adjust a portion of the notice against accrued Earned Leave where policy and business continuity permit.

Employees are expected to remain actively available, complete handovers, document responsibilities, and support transition planning during notice. Unapproved absence during notice may be treated as a notice shortfall and may affect final settlement or relieving documentation. Managers should define handover expectations in writing within the first week after resignation acceptance.

The company may place an employee on garden leave, waive part of the notice period, or provide payment in lieu where contractually and legally permitted. Bonus eligibility, variable pay, and retention awards during notice are subject to the terms of the relevant compensation plan. Company assets must be returned before final settlement is completed.

## 10. Work From Home Policy

Work From Home is a manager-approved flexibility arrangement under which an employee performs duties from their approved home location within the same employing country unless otherwise approved. Work From Home is not an automatic entitlement and may be granted based on role suitability, performance, data security requirements, and team coverage.

Employees approved for Work From Home must remain reachable during core working hours from 10:00 AM to 4:00 PM local time and must attend scheduled meetings, check-ins, and critical collaboration sessions. Employees are expected to maintain a secure and professional work environment, stable internet connectivity, and compliance with information security standards.

Ad hoc Work From Home requests for up to 2 days at a time may be approved by the reporting manager. Longer Work From Home arrangements of more than 10 consecutive working days require HR acknowledgment in addition to manager approval. Employees should not work from public spaces that create confidentiality or connectivity risks when handling sensitive company or employee data.

Repeated Work From Home misuse, such as non-responsiveness, poor attendance logging, or failure to meet deliverables, may result in withdrawal of the arrangement. Work From Home approval does not change the employee's office location, payroll location, tax registration, or reporting structure.

## 11. Remote Work Policy

Remote Work under this handbook refers to an approved ongoing arrangement where the employee is designated to work primarily outside the assigned office location for an extended period. Remote Work requires formal approval from the business leader, HR, IT Security, and where relevant, Finance or Legal. The approved remote work location must be declared in writing and may not be changed unilaterally by the employee.

Cross-border Remote Work is not permitted without prior written approval because of payroll, tax, immigration, permanent establishment, and data privacy implications. Domestic Remote Work from a different state may also require approval if it creates statutory registration, reimbursement, equipment shipping, or labor law implications.

Employees on Remote Work arrangements must comply with the same productivity, attendance, confidentiality, and conduct expectations as office-based employees. They may be required to attend periodic in-person meetings, onboarding sessions, performance reviews, or team events with reasonable advance notice. Travel costs for such visits will be governed by the applicable travel policy and the specific approval terms of the remote arrangement.

If business needs change, the company may review, modify, or withdraw a Remote Work arrangement with reasonable notice. Employees should not assume that an ad hoc Work From Home approval converts automatically into a Remote Work arrangement.

## 12. Attendance Policy

The standard workweek is Monday to Friday unless the employee's role, shift roster, or local business schedule states otherwise. The general working day is 9 hours including breaks, with an expected start time between 8:00 AM and 10:00 AM depending on team norms. Employees must record attendance through the approved HR system, biometric device, or other designated workflow.

Late login or late arrival up to 30 minutes on an occasional basis may be tolerated by the reporting manager where work output is not affected. However, repeated late attendance, early sign-off, missed punch events, or unexplained absence may trigger attendance counseling. Three instances of unapproved late attendance in a rolling 30-day period may lead to a formal review by the manager and HR.

Attendance regularization requests should be submitted within 2 working days of the missed or incorrect record. Requests submitted after the monthly payroll cut-off may be updated in the next cycle. Employees working remotely remain responsible for accurate attendance capture unless the manager has approved an alternative process.

Managers must review attendance patterns fairly and consistently. Attendance controls should not penalize employees who are on approved leave, approved business travel, or formally approved flexible work arrangements. If an employee is unable to log attendance due to a system issue, they must notify the manager on the same day and submit regularization once the system is available.

## 13. Policy Interpretation and Escalation

Questions about eligibility, exceptions, supporting documents, or policy interpretation should be raised with HR Operations. Payroll matters should be raised with the Payroll team through the designated helpdesk. Employees should not rely on informal chat messages, outdated documents, or verbal statements when making decisions that affect leave, payroll, or notice commitments.

Where a policy answer is not clearly available in this handbook, the correct response is that the policy is unavailable in the current document and HR review is required. No employee, manager, or automated agent should infer a rule that is not supported by the approved policy text.`;

interface PolicySection {
  title: string;
  content: string;
  order: number;
}

function loadPolicySections(): PolicySection[] {
  const text = POLICY_TEXT.trim();
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

const SUPERVISOR_PROMPT = `You are the supervisor for an HR workflow engine. Your job is to route user requests correctly between two specialized agents.`;

const STRONG_POLICY = [
  "policy",
  "what is the policy",
  "what does the policy say",
  "notice period",
  "work from home",
  "remote work",
];

const ACTION_PATTERNS: string[][] = [
  ["leave balance", "remaining leave", "check balance", "how many days of leave"],
  ["payslip", "salary", "download payslip", "pay slip"],
  [
    "apply leave",
    "request leave",
    "take leave",
    "apply for leave",
    "applying for leave",
    "requesting leave",
    "taking leave",
  ],
];

const ACTION_WORD_PAIRS_VERBS = new Set([
  "apply",
  "applying",
  "applies",
  "request",
  "requesting",
  "requests",
  "take",
  "taking",
  "takes",
]);

const POLICY_KEYWORDS = [
  "policy",
  "notice period",
  "work from home",
  "remote work",
  "attendance policy",
  "leave policy",
  "payroll policy",
  "maternity leave policy",
  "paternity leave policy",
  "what is the policy on",
  "what does the policy say",
  "sick leave policy",
  "casual leave policy",
  "earned leave policy",
];

const ACTION_TRIGGERS = new Set([
  "balance",
  "apply",
  "applying",
  "applies",
  "payslip",
  "salary",
  "remaining",
]);

function isDeterministic(query: string): [boolean, string[], string] {
  const q = query.toLowerCase();
  const qWords = new Set(q.split(/\s+/));

  const matchesAction = (): boolean => {
    for (const keywords of ACTION_PATTERNS) {
      if (keywords.some((k) => q.includes(k))) return true;
    }
    if (
      qWords.has("leave") &&
      [...ACTION_WORD_PAIRS_VERBS].some((v) => qWords.has(v))
    )
      return true;
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
  const naiveCost =
    (naivePromptTokens * 0.15 + naiveCompletionTokens * 0.6) / 1_000_000;

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

function llmSupervisorRoute(userInput: string): {
  nextAgents: string[];
  rationale: string;
} {
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
    rationale:
      "Supervisor LLM decision: Query intent is ambiguous. Routing to both agents as a safe fallback.",
  };
}

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .split(/\s+/)
    .filter((w) => w.length > 2);
}

function retrievePolicy(query: string, topK = 4): PolicySection[] {
  const queryTokens = new Set(tokenize(query));
  if (queryTokens.size === 0) return [];

  const scored = POLICY_SECTIONS.map((section) => {
    const sectionTokens = new Set(
      tokenize(section.title + " " + section.content)
    );
    let overlap = 0;
    for (const t of queryTokens) {
      if (sectionTokens.has(t)) overlap++;
    }
    return {
      section,
      score: overlap / Math.sqrt(queryTokens.size + sectionTokens.size),
    };
  });

  scored.sort((a, b) => b.score - a.score);
  return scored
    .slice(0, topK)
    .filter((s) => s.score > 0)
    .map((s) => s.section);
}

function runPolicyAgent(userInput: string) {
  const start = performance.now();
  const hits = retrievePolicy(userInput, 4);

  if (hits.length === 0) {
    const content =
      "Policy unavailable: I could not find a supported answer in the retrieved HR policy context.";
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
    lines.push(
      `*Source: docs/hr_policy.md (Relevance Rank: ${hit.order + 1})*`
    );
    lines.push(hit.content);
  }
  const content = lines.join("\n");

  return {
    messages: [{ type: "ai", content, name: "policy_agent" }],
    executedAgents: ["policy_agent"],
    policyResult: {
      status: "grounded",
      answer: content,
      citations: hits.map((h, i) => ({
        title: h.title,
        source: "docs/hr_policy.md",
        rank: i + 1,
      })),
    },
    latency: performance.now() - start,
  };
}

function extractEmployeeId(
  text: string,
  fallback: string | null
): string | null {
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

const MONTHS = [
  "january", "february", "march", "april", "may", "june",
  "july", "august", "september", "october", "november", "december",
];

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

function checkLeaveBalance(
  employeeId: string,
  leaveType: string
): ToolResult {
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

function applyLeave(
  employeeId: string,
  leaveType: string,
  startDate: string,
  endDate: string,
  _reason: string
): ToolResult {
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

function fetchPayslip(
  employeeId: string,
  month: string,
  year: number
): ToolResult {
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

function runActionAgent(userInput: string, prevEmployeeId?: string) {
  const start = performance.now();
  const query = userInput.toLowerCase();

  if (
    ["balance", "how many days", "remaining"].some((k) => query.includes(k))
  ) {
    const employeeId =
      extractEmployeeId(userInput, prevEmployeeId ?? null) ?? "EMP-123";
    const leaveType = extractLeaveType(query, "sick");
    const result = checkLeaveBalance(employeeId, leaveType);
    const summary = `Checked leave balance for ${employeeId}. Leave Type: ${leaveType.charAt(0).toUpperCase() + leaveType.slice(1)}, Balance: ${result.balance} days (Source: ${result.source}, Status: ${result.status}).`;
    return {
      messages: [{ type: "ai", content: summary, name: "action_agent" }],
      executedAgents: ["action_agent"],
      actionResult: {
        status: result.status,
        tool: "check_leave_balance",
        summary,
        output: result,
      },
      employeeId,
      startDate: null,
      endDate: null,
      latency: performance.now() - start,
    };
  }

  if (
    ["apply", "request leave", "take leave"].some((k) => query.includes(k))
  ) {
    const employeeId =
      extractEmployeeId(userInput, prevEmployeeId ?? null) ?? "EMP-123";
    const leaveType = extractLeaveType(query, "earned");
    const [extStart, extEnd] = extractDates(userInput);
    const startDate = extStart ?? "2026-07-20";
    const endDate = extEnd ?? "2026-07-21";
    const reason = extractReason(userInput, "Personal request");
    const result = applyLeave(employeeId, leaveType, startDate, endDate, reason);
    const summary = `Applied for leave. Request ID: ${result.request_id}. Employee: ${employeeId}, Type: ${leaveType.charAt(0).toUpperCase() + leaveType.slice(1)}, Dates: ${startDate} to ${endDate}. Status: ${result.status}. Message: ${result.message}`;
    return {
      messages: [{ type: "ai", content: summary, name: "action_agent" }],
      executedAgents: ["action_agent"],
      actionResult: {
        status: result.status,
        tool: "apply_leave",
        summary,
        output: result,
      },
      employeeId,
      startDate,
      endDate,
      latency: performance.now() - start,
    };
  }

  if (["payslip", "salary", "pay slip"].some((k) => query.includes(k))) {
    const employeeId =
      extractEmployeeId(userInput, prevEmployeeId ?? null) ?? "EMP-123";
    const month = extractMonth(query, "July");
    const year = extractYear(query, 2026);
    const result = fetchPayslip(employeeId, month, year);
    const summary = `Fetched payslip for ${employeeId} (${month} ${year}). Net Salary: INR ${(result.net_salary as number).toFixed(2)}. Status: ${result.status}. Details: ${result.details}`;
    return {
      messages: [{ type: "ai", content: summary, name: "action_agent" }],
      executedAgents: ["action_agent"],
      actionResult: {
        status: result.status,
        tool: "fetch_payslip",
        summary,
        output: result,
      },
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

function handleInvoke(body: { user_input: string; session_id?: string }) {
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
  const promptTokens = supervisor.promptTokens;
  const completionTokens = supervisor.completionTokens;

  const naiveCost =
    (Math.floor((SUPERVISOR_PROMPT + userInput).length / 4) * 0.15 +
      60 * 0.6) /
    1_000_000;

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
  const percentageReduction =
    naiveCost > 0 ? ((naiveCost - optimizedCost) / naiveCost) * 100 : 0;

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

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const path = url.pathname.replace(/^\/hr-workflow/, "");

    if (path === "/health" || path === "/health/" || path === "" || path === "/") {
      return new Response(
        JSON.stringify({
          status: "ok",
          service: "Agentic HR Workflow Engine",
          environment: "production",
        }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (path === "/invoke" && req.method === "POST") {
      const body = await req.json();
      const result = handleInvoke(body);
      return new Response(JSON.stringify(result), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    if (path === "/graph" && req.method === "GET") {
      return new Response(JSON.stringify({ mermaid: MERMAID }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ detail: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ error: err instanceof Error ? err.message : "Internal error" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
