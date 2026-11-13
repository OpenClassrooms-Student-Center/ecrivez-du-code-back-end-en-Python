from collections.abc import Callable
from datetime import date
from enum import Enum, auto
from typing import Protocol

from .models import Employee, LeaveRequest
from .policies import ContractType, LeavePolicyResolver


class ApprovalResult(Enum):
    APPROVED = auto()
    INSUFFICIENT_BALANCE = auto()
    NOT_FOUND = auto()


class LeaveNotifier(Protocol):
    def notify(self, employee: Employee, message: str) -> None: ...


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

    def approve(self, request_id: int) -> ApprovalResult:
        # Filtrage en Python conservé : il sera confié à la base au chapitre 4.
        matching = [r for r in LeaveRequest.objects.all() if r.id == request_id]
        if not matching:
            return ApprovalResult.NOT_FOUND
        leave_request = matching[0]
        employee = leave_request.employee

        if self._compute_balance(employee) < leave_request.working_days:
            leave_request.status = "Refused"
            leave_request.save()
            return ApprovalResult.INSUFFICIENT_BALANCE

        leave_request.status = "Approved"
        leave_request.save()
        employee.days_taken += leave_request.working_days
        employee.save()

        self._notifier.notify(employee, "Votre demande de congés est approuvée.")
        return ApprovalResult.APPROVED

    def _compute_balance(self, employee: Employee) -> float:
        contract_type = ContractType(employee.contract_type)
        policy = self._policies.policy_for(contract_type)
        return policy.compute_entitlement(employee, self._today()) - employee.days_taken
