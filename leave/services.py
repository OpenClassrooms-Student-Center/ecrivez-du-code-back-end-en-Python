from collections.abc import Callable
from datetime import date, timedelta
from enum import Enum, auto
from typing import Protocol

from django.db import transaction
from django.db.models import QuerySet

from .models import Employee, LeaveRequest, LeaveStatus
from .policies import ContractType, LeavePolicyResolver


class ApprovalResult(Enum):
    APPROVED = auto()
    INSUFFICIENT_BALANCE = auto()
    NOT_FOUND = auto()
    NOT_PENDING = auto()


class RefusalResult(Enum):
    REFUSED = auto()
    NOT_FOUND = auto()
    NOT_PENDING = auto()


class LeaveNotifier(Protocol):
    def notify(self, employee: Employee, message: str) -> None: ...


def count_working_days(start_date: date, end_date: date) -> int:
    """Compte les jours du lundi au vendredi, bornes incluses (jours fériés ignorés)."""
    days = (end_date - start_date).days + 1
    all_days = (start_date + timedelta(days=offset) for offset in range(days))
    return sum(1 for day in all_days if day.weekday() < 5)


class LeaveService:
    def __init__(
        self,
        policies: LeavePolicyResolver,
        notifier: LeaveNotifier,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._policies = policies
        self._notifier = notifier
        self._today = today

    def get_balance(self, employee_id: int) -> float | None:
        employee = Employee.objects.filter(pk=employee_id).first()
        if employee is None:
            return None
        return self._compute_balance(employee)

    def get_requests(self, status: str | None = None) -> QuerySet[LeaveRequest]:
        leave_requests = LeaveRequest.objects.order_by("start_date")
        if status is not None:
            leave_requests = leave_requests.filter(status=status)
        return leave_requests

    def get_request(self, request_id: int) -> LeaveRequest | None:
        return LeaveRequest.objects.filter(pk=request_id).first()

    def create(
        self, employee_id: int, start_date: date, end_date: date
    ) -> LeaveRequest | None:
        if not Employee.objects.filter(pk=employee_id).exists():
            return None
        return LeaveRequest.objects.create(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            working_days=count_working_days(start_date, end_date),
        )

    @transaction.atomic
    def approve(self, request_id: int) -> ApprovalResult:
        leave_request = (
            LeaveRequest.objects.select_related("employee")
            .filter(pk=request_id)
            .first()
        )
        if leave_request is None:
            return ApprovalResult.NOT_FOUND
        if leave_request.status != LeaveStatus.PENDING:
            return ApprovalResult.NOT_PENDING
        employee = leave_request.employee

        if self._compute_balance(employee) < leave_request.working_days:
            leave_request.status = LeaveStatus.REFUSED
            leave_request.save()
            return ApprovalResult.INSUFFICIENT_BALANCE

        leave_request.status = LeaveStatus.APPROVED
        leave_request.save()
        employee.days_taken += leave_request.working_days
        employee.save()

        self._notifier.notify(employee, "Votre demande de congés est approuvée.")
        return ApprovalResult.APPROVED

    @transaction.atomic
    def refuse(self, request_id: int) -> RefusalResult:
        leave_request = LeaveRequest.objects.filter(pk=request_id).first()
        if leave_request is None:
            return RefusalResult.NOT_FOUND
        if leave_request.status != LeaveStatus.PENDING:
            return RefusalResult.NOT_PENDING

        leave_request.status = LeaveStatus.REFUSED
        leave_request.save()
        return RefusalResult.REFUSED

    def _compute_balance(self, employee: Employee) -> float:
        contract_type = ContractType(employee.contract_type)
        policy = self._policies.policy_for(contract_type)
        return policy.compute_entitlement(employee, self._today()) - employee.days_taken
