"""Mock HR tools with built-in resilience (retry, timeout, fallback) and metadata tracking."""

import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any

from pydantic import BaseModel, Field

from backend.tracing.logging import get_logger

logger = get_logger(__name__)


# ----------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------


class LeaveBalanceRequest(BaseModel):
    employee_id: str = Field(..., description="The unique ID of the employee.")
    leave_type: str = Field(..., description="Type of leave (e.g., sick, casual, earned).")


class LeaveBalanceResponse(BaseModel):
    status: str = Field(..., description="Status of the check (e.g., success, fallback).")
    employee_id: str
    leave_type: str
    balance: int
    source: str = Field(..., description="Source of data (e.g., api, fallback_cache).")


class ApplyLeaveRequest(BaseModel):
    employee_id: str = Field(..., description="The unique ID of the employee.")
    leave_type: str = Field(..., description="Type of leave (e.g., sick, casual, earned).")
    start_date: str = Field(..., description="Start date of leave (YYYY-MM-DD).")
    end_date: str = Field(..., description="End date of leave (YYYY-MM-DD).")
    reason: str = Field(..., description="Reason for applying.")


class ApplyLeaveResponse(BaseModel):
    status: str = Field(
        ...,
        description="Status of the application (e.g., approved, pending, fallback_queued).",
    )
    request_id: str
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    message: str


class FetchPayslipRequest(BaseModel):
    employee_id: str = Field(..., description="The unique ID of the employee.")
    month: str = Field(..., description="Month of payslip.")
    year: int = Field(..., description="Year of payslip.")


class FetchPayslipResponse(BaseModel):
    status: str = Field(..., description="Status of the call (e.g., success, fallback).")
    employee_id: str
    month: str
    year: int
    net_salary: float
    details: str


# ----------------------------------------------------
# Core System APIs (Mocking database and latency)
# ----------------------------------------------------


def _core_check_leave_balance(request: LeaveBalanceRequest) -> LeaveBalanceResponse:
    # Simulate latency
    latency = random.uniform(0.1, 1.2)
    time.sleep(latency)

    # Simulate random failure
    if random.random() < 0.3:
        raise RuntimeError("HR Database timeout.")

    balances = {"sick": 10, "casual": 8, "earned": 15}
    bal = balances.get(request.leave_type.lower(), 12)
    return LeaveBalanceResponse(
        status="success",
        employee_id=request.employee_id,
        leave_type=request.leave_type,
        balance=bal,
        source="api",
    )


def _fallback_check_leave_balance(request: LeaveBalanceRequest) -> LeaveBalanceResponse:
    return LeaveBalanceResponse(
        status="fallback",
        employee_id=request.employee_id,
        leave_type=request.leave_type,
        balance=10,
        source="fallback_cache",
    )


def _core_apply_leave(request: ApplyLeaveRequest) -> ApplyLeaveResponse:
    # Simulate latency
    latency = random.uniform(0.1, 1.2)
    time.sleep(latency)

    # Simulate random failure
    if random.random() < 0.3:
        raise RuntimeError("HR API write conflict.")

    request_id = str(uuid.uuid4())
    return ApplyLeaveResponse(
        status="approved",
        request_id=request_id,
        employee_id=request.employee_id,
        leave_type=request.leave_type,
        start_date=request.start_date,
        end_date=request.end_date,
        message="Leave application approved automatically.",
    )


def _fallback_apply_leave(request: ApplyLeaveRequest) -> ApplyLeaveResponse:
    return ApplyLeaveResponse(
        status="fallback_queued",
        request_id="FALLBACK-" + str(uuid.uuid4())[:8],
        employee_id=request.employee_id,
        leave_type=request.leave_type,
        start_date=request.start_date,
        end_date=request.end_date,
        message="HR API offline. Leave request queued for manual administrator review.",
    )


def _core_fetch_payslip(request: FetchPayslipRequest) -> FetchPayslipResponse:
    # Simulate latency
    latency = random.uniform(0.1, 1.2)
    time.sleep(latency)

    # Simulate random failure
    if random.random() < 0.3:
        raise RuntimeError("HR API payroll gateway error.")

    return FetchPayslipResponse(
        status="success",
        employee_id=request.employee_id,
        month=request.month,
        year=request.year,
        net_salary=85000.0,
        details="Basic: 50000, Allowances: 40000, Deductions: 5000",
    )


def _fallback_fetch_payslip(request: FetchPayslipRequest) -> FetchPayslipResponse:
    return FetchPayslipResponse(
        status="fallback",
        employee_id=request.employee_id,
        month=request.month,
        year=request.year,
        net_salary=0.0,
        details="HR API offline. Payslip details unavailable. Please try again later.",
    )


# ----------------------------------------------------
# Resilience Execution Engine
# ----------------------------------------------------


def execute_with_resilience(
    core_func: Any,
    request: Any,
    fallback_func: Any,
    timeout_sec: float = 0.8,
    max_retries: int = 2,
) -> tuple[Any, dict[str, Any]]:
    """Execute a task with thread-pool timeout and retry-fallback mechanisms."""
    failures: list[str] = []
    start_time = time.perf_counter()
    attempts = 0

    with ThreadPoolExecutor(max_workers=1) as executor:
        for attempt in range(1, max_retries + 1):
            attempts = attempt
            try:
                future = executor.submit(core_func, request)
                result = future.result(timeout=timeout_sec)
                elapsed = time.perf_counter() - start_time
                metadata = {
                    "latency_sec": elapsed,
                    "retries": attempt - 1,
                    "failures": failures,
                }
                logger.info(
                    "tool_execution_attempt_success",
                    tool=core_func.__name__,
                    attempt=attempt,
                    latency_sec=elapsed,
                )
                return result, metadata
            except TimeoutError:
                failures.append(f"Timeout after {timeout_sec}s")
                logger.warning(
                    "tool_execution_attempt_timeout",
                    tool=core_func.__name__,
                    attempt=attempt,
                    timeout_sec=timeout_sec,
                )
            except Exception as e:
                failures.append(str(e))
                logger.warning(
                    "tool_execution_attempt_failed",
                    tool=core_func.__name__,
                    attempt=attempt,
                    error=str(e),
                )

    result = fallback_func(request)
    elapsed = time.perf_counter() - start_time
    metadata = {
        "latency_sec": elapsed,
        "retries": attempts - 1,
        "failures": failures,
    }
    logger.info(
        "tool_execution_fallback_activated",
        tool=core_func.__name__,
        fallback_tool=fallback_func.__name__,
        latency_sec=elapsed,
        retries=attempts - 1,
        failures=failures,
    )
    return result, metadata


# ----------------------------------------------------
# Public Tool Interfaces
# ----------------------------------------------------


def check_leave_balance(employee_id: str, leave_type: str) -> dict[str, Any]:
    """Check leave balance for an employee with resilience."""
    req = LeaveBalanceRequest(employee_id=employee_id, leave_type=leave_type)
    res, metadata = execute_with_resilience(
        core_func=_core_check_leave_balance,
        request=req,
        fallback_func=_fallback_check_leave_balance,
    )
    return {
        "status": res.status,
        "employee_id": res.employee_id,
        "leave_type": res.leave_type,
        "balance": res.balance,
        "source": res.source,
        "trace_metadata": metadata,
    }


def apply_leave(
    employee_id: str, leave_type: str, start_date: str, end_date: str, reason: str
) -> dict[str, Any]:
    """Apply for leave for an employee with resilience."""
    req = ApplyLeaveRequest(
        employee_id=employee_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
    )
    res, metadata = execute_with_resilience(
        core_func=_core_apply_leave,
        request=req,
        fallback_func=_fallback_apply_leave,
    )
    return {
        "status": res.status,
        "request_id": res.request_id,
        "employee_id": res.employee_id,
        "leave_type": res.leave_type,
        "start_date": res.start_date,
        "end_date": res.end_date,
        "message": res.message,
        "trace_metadata": metadata,
    }


def fetch_payslip(employee_id: str, month: str, year: int) -> dict[str, Any]:
    """Fetch payslip for an employee with resilience."""
    req = FetchPayslipRequest(employee_id=employee_id, month=month, year=year)
    res, metadata = execute_with_resilience(
        core_func=_core_fetch_payslip,
        request=req,
        fallback_func=_fallback_fetch_payslip,
    )
    return {
        "status": res.status,
        "employee_id": res.employee_id,
        "month": res.month,
        "year": res.year,
        "net_salary": res.net_salary,
        "details": res.details,
        "trace_metadata": metadata,
    }
