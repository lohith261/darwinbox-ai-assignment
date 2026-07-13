"""Unit tests for resilient HR tools and ActionAgent."""

import time
from typing import Any

from backend.agents.action import ActionAgent
from backend.tools.hr_tools import (
    LeaveBalanceRequest,
    LeaveBalanceResponse,
    execute_with_resilience,
)


def test_execute_with_resilience_success() -> None:
    def core_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="success",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=15,
            source="api",
        )

    def fallback_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="fallback",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=10,
            source="fallback_cache",
        )

    req = LeaveBalanceRequest(employee_id="EMP-123", leave_type="sick")
    res, _ = execute_with_resilience(
        core_func=core_func,
        request=req,
        fallback_func=fallback_func,
    )
    assert res.status == "success"
    assert res.balance == 15
    assert res.source == "api"


def test_execute_with_resilience_failure_fallback() -> None:
    # A core function that always raises an error
    def core_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        raise RuntimeError("Persistent database failure")

    def fallback_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="fallback",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=10,
            source="fallback_cache",
        )

    req = LeaveBalanceRequest(employee_id="EMP-123", leave_type="sick")
    res, _ = execute_with_resilience(
        core_func=core_func,
        request=req,
        fallback_func=fallback_func,
        max_retries=2,
    )
    assert res.status == "fallback"
    assert res.balance == 10
    assert res.source == "fallback_cache"


def test_execute_with_resilience_timeout_fallback() -> None:
    # A core function that is very slow (exceeds timeout)
    def core_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        time.sleep(0.5)
        return LeaveBalanceResponse(
            status="success",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=15,
            source="api",
        )

    def fallback_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="fallback",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=10,
            source="fallback_cache",
        )

    req = LeaveBalanceRequest(employee_id="EMP-123", leave_type="sick")
    res, _ = execute_with_resilience(
        core_func=core_func,
        request=req,
        fallback_func=fallback_func,
        timeout_sec=0.1,  # Short timeout to force fallback
        max_retries=1,
    )
    assert res.status == "fallback"
    assert res.balance == 10


def test_execute_with_resilience_retry_success() -> None:
    call_count = 0

    # A core function that fails on the first call, succeeds on the second
    def core_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("Temporary glitch")
        return LeaveBalanceResponse(
            status="success",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=15,
            source="api",
        )

    def fallback_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="fallback",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=10,
            source="fallback_cache",
        )

    req = LeaveBalanceRequest(employee_id="EMP-123", leave_type="sick")
    res, _ = execute_with_resilience(
        core_func=core_func,
        request=req,
        fallback_func=fallback_func,
        max_retries=2,
    )
    assert res.status == "success"
    assert res.balance == 15
    assert call_count == 2


def test_action_agent_check_leave_balance() -> None:
    agent = ActionAgent()
    result: Any = agent.run("Please check my casual leave balance for EMP-456")

    assert result["executed_agents"] == ["action_agent"]
    action_result = result["action_result"]
    assert action_result["tool"] == "check_leave_balance"
    assert action_result["output"]["employee_id"] == "EMP-456"
    assert action_result["output"]["leave_type"] == "casual"
    assert "balance" in action_result["output"]


def test_action_agent_apply_leave() -> None:
    agent = ActionAgent()
    result: Any = agent.run(
        "Apply for sick leave for EMP-789 from 2026-08-10 to 2026-08-12 because of fever"
    )

    assert result["executed_agents"] == ["action_agent"]
    action_result = result["action_result"]
    assert action_result["tool"] == "apply_leave"
    assert action_result["output"]["employee_id"] == "EMP-789"
    assert action_result["output"]["leave_type"] == "sick"
    assert action_result["output"]["start_date"] == "2026-08-10"
    assert action_result["output"]["end_date"] == "2026-08-12"
    assert "request_id" in action_result["output"]


def test_action_agent_fetch_payslip() -> None:
    agent = ActionAgent()
    result: Any = agent.run("Get the payslip for June 2025 for employee EMP-002")

    assert result["executed_agents"] == ["action_agent"]
    action_result = result["action_result"]
    assert action_result["tool"] == "fetch_payslip"
    assert action_result["output"]["employee_id"] == "EMP-002"
    assert action_result["output"]["month"] == "June"
    assert action_result["output"]["year"] == 2025
    assert "net_salary" in action_result["output"]
