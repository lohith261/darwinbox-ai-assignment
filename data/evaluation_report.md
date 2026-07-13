# Darwin HR Workflow Engine Evaluation Report

## Performance Metrics & Telemetry Results

| Test Case Name | Status | Total Latency (s) | Prompt Tokens | Completion Tokens | Total Cost | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Happy Path: Balance Check | 🟢 PASS | 0.492s | 0 | 0 | $0.000000 | Balance check executed successfully. |
| Happy Path: Apply Leave | 🟢 PASS | 0.989s | 117 | 60 | $0.000054 | Leave application executed successfully. |
| Happy Path: Fetch Payslip | 🟢 PASS | 1.368s | 0 | 0 | $0.000000 | Payslip download executed successfully. |
| Happy Path: Policy QA | 🟢 PASS | 0.320s | 110 | 60 | $0.000053 | Policy QA succeeded with citation list. |
| Invalid Leave Request (Missing Dates) | 🟢 PASS | 0.379s | 0 | 0 | $0.000000 | Leave application executed successfully. |
| Invalid Leave Request (Invalid Range) | 🟢 PASS | 0.810s | 0 | 0 | $0.000000 | Handled invalid date ranges with queued state successfully. |
| Missing Policy Information | 🟢 PASS | 0.302s | 112 | 60 | $0.000053 | Correctly returned 'Policy unavailable' for missing policies. |
| Ambiguous Query | 🟢 PASS | 0.289s | 106 | 60 | $0.000052 | Correctly fell back to unsupported status for ambiguous query. |
| Gibberish Input | 🟢 PASS | 0.301s | 105 | 60 | $0.000052 | Gibberish query safely triggered fallback/unsupported status. |
| Memory: Employee ID turn | 🟢 PASS | 3.480s | 0 | 0 | $0.000000 | Employee ID preserved successfully across turns. |
| Memory: Date turn | 🟢 PASS | 3.042s | 234 | 120 | $0.000107 | Leave dates preserved successfully across turns. |
| RAG Retrieval Edge Case | 🟢 PASS | 0.283s | 115 | 60 | $0.000053 | Filtered out low-confidence RAG lookup successfully. |
| Tool Resilience Fallback | 🟢 PASS | 1.709s | 0 | 0 | $0.000000 | Resilience loop correctly activated fallback cached logic. |
| Compound Request | 🟢 PASS | 0.287s | 126 | 60 | $0.000055 | Supervisor routed compound query successfully. |
| SQL Injection Attempt | 🟢 PASS | 0.542s | 0 | 0 | $0.000000 | Safe parsing prevented SQL injection execution. |

### Summary Statistics
- **Total Test Cases:** 15
- **Passed:** 15
- **Failed:** 0
- **Success Rate:** 100.0%