"""Action agent implementation executing mock resilient HR tools with conversation memory."""

import re
from dataclasses import dataclass
from typing import Any, cast

from langchain_core.messages import AIMessage

from backend.tools.hr_tools import apply_leave, check_leave_balance, fetch_payslip


@dataclass(slots=True)
class ActionAgent:
    """Executes approved HR workflow actions via mock resilient HR tools."""

    name: str = "action_agent"

    def run(self, state: Any) -> dict[str, object]:
        """Parse user query, invoke resilient tools, and return execution results."""
        if isinstance(state, dict):
            state_dict = cast(dict[str, Any], state)
            user_input = state_dict.get("user_input", "")
            employee_id = state_dict.get("employee_id", "")
            start_date = state_dict.get("start_date", "")
            end_date = state_dict.get("end_date", "")
            prev_action = state_dict.get("action_result")
        else:
            user_input = str(state)
            employee_id = ""
            start_date = ""
            end_date = ""
            prev_action = None

        query = user_input.lower()
        prev_tool = None
        if isinstance(prev_action, dict):
            prev_tool = prev_action.get("tool")

        # Check if the query is a modification of a previous action
        is_leave_modification = False
        is_balance_modification = False

        if prev_tool == "apply_leave" and any(
            lt in query for lt in ["sick", "casual", "earned", "change", "instead"]
        ):
            is_leave_modification = True

        elif prev_tool == "check_leave_balance" and any(
            lt in query for lt in ["sick", "casual", "earned"]
        ):
            is_balance_modification = True

        # 1. Check Leave Balance Intent
        if (
            "balance" in query
            or "how many days" in query
            or "remaining" in query
            or is_balance_modification
        ):
            employee_id = self._extract_employee_id(user_input, employee_id) or "EMP-123"
            leave_type = self._extract_leave_type(query, "sick")
            result = check_leave_balance(employee_id=employee_id, leave_type=leave_type)
            summary = (
                f"Checked leave balance for {employee_id}. "
                f"Leave Type: {result['leave_type'].capitalize()}, "
                f"Balance: {result['balance']} days "
                f"(Source: {result['source']}, Status: {result['status']})."
            )
            response = self._build_response(summary, "check_leave_balance", result)
            response.update(
                {
                    "employee_id": employee_id,
                }
            )
            return response

        # 2. Apply Leave Intent
        elif (
            "apply" in query
            or "request leave" in query
            or "take leave" in query
            or is_leave_modification
        ):
            employee_id = self._extract_employee_id(user_input, employee_id) or "EMP-123"
            leave_type = self._extract_leave_type(query, "earned")
            ext_start, ext_end = self._extract_dates(user_input)
            if ext_start and ext_end:
                start_date = ext_start
                end_date = ext_end
            else:
                start_date = start_date or "2026-07-20"
                end_date = end_date or "2026-07-21"

            reason = self._extract_reason(user_input, "Personal request")
            result = apply_leave(
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
            )
            summary = (
                f"Applied for leave. Request ID: {result['request_id']}. "
                f"Employee: {employee_id}, Type: {leave_type.capitalize()}, "
                f"Dates: {start_date} to {end_date}. Status: {result['status']}. "
                f"Message: {result['message']}"
            )
            response = self._build_response(summary, "apply_leave", result)
            response.update(
                {
                    "employee_id": employee_id,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
            return response

        # 3. Fetch Payslip Intent
        elif "payslip" in query or "salary" in query or "pay slip" in query:
            employee_id = self._extract_employee_id(user_input, employee_id) or "EMP-123"
            month = self._extract_month(query, "July")
            year = self._extract_year(query, 2026)
            result = fetch_payslip(employee_id=employee_id, month=month, year=year)
            summary = (
                f"Fetched payslip for {employee_id} ({month} {year}). "
                f"Net Salary: INR {result['net_salary']:.2f}. "
                f"Status: {result['status']}. Details: {result['details']}"
            )
            response = self._build_response(summary, "fetch_payslip", result)
            response.update(
                {
                    "employee_id": employee_id,
                }
            )
            return response

        # 4. Fallback Intent
        summary = f"ActionAgent could not determine a matching HR tool for: {user_input}"
        return {
            "messages": [AIMessage(content=summary, name=self.name)],
            "executed_agents": [self.name],
            "action_result": {
                "status": "unsupported",
                "summary": summary,
            },
        }

    def _extract_employee_id(self, text: str, default: str | None) -> str | None:
        """Parse Employee ID pattern (EMP-XXXX) from query text, defaulting if missing."""
        match = re.search(r"\b(EMP-?\d+)\b", text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return default if default else None

    def _extract_leave_type(self, text: str, default: str) -> str:
        """Parse leave type keyword (sick, casual, earned) from text."""
        for ltype in ["sick", "casual", "earned"]:
            if ltype in text:
                return ltype
        return default

    def _extract_dates(self, text: str) -> tuple[str | None, str | None]:
        """Extract YYYY-MM-DD date ranges from input text."""
        dates = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        if len(dates) >= 2:
            return dates[0], dates[1]
        elif len(dates) == 1:
            return dates[0], dates[0]
        return None, None

    def _extract_reason(self, text: str, default: str) -> str:
        """Extract application reason context from text."""
        match = re.search(r"(?:reason|due to|because of)\s+([^.]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return default

    def _extract_month(self, text: str, default: str) -> str:
        """Extract calendar month keyword from text."""
        months = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
        for m in months:
            if m in text:
                return m.capitalize()
        return default

    def _extract_year(self, text: str, default: int) -> int:
        """Extract year digits from text."""
        match = re.search(r"\b(20\d{2})\b", text)
        if match:
            return int(match.group(1))
        return default

    def _build_response(
        self, summary: str, tool_name: str, tool_output: dict[str, Any]
    ) -> dict[str, object]:
        """Build standard API execution dictionary containing structured tool metrics."""
        return {
            "messages": [AIMessage(content=summary, name=self.name)],
            "executed_agents": [self.name],
            "action_result": {
                "status": tool_output.get("status", "success"),
                "tool": tool_name,
                "summary": summary,
                "output": tool_output,
            },
        }
