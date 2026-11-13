import math
from typing import assert_never

from django.http import JsonResponse

from .notifications import NotificationService
from .policies import (
    ApprenticeshipPolicy,
    ContractType,
    FixedTermContractPolicy,
    LeavePolicyResolver,
    PermanentContractPolicy,
)
from .services import ApprovalResult, LeaveService


def _build_leave_service() -> LeaveService:
    # Assemblage provisoire : il sera déplacé au chapitre 4.
    policies = LeavePolicyResolver({
        ContractType.PERMANENT: PermanentContractPolicy(),
        ContractType.FIXED_TERM: FixedTermContractPolicy(),
        ContractType.APPRENTICESHIP: ApprenticeshipPolicy(),
    })
    return LeaveService(policies, NotificationService())


def balance(request):
    # Contrat de l’API inchangé jusqu’au chapitre 5.
    employee_id = request.GET.get("employeeId", "")
    result = None
    if employee_id.isdigit():
        result = _build_leave_service().get_balance(int(employee_id))
    if result is None:
        return JsonResponse({"error": "Employee not found"})
    return JsonResponse({"employeeId": int(employee_id), "balance": result})


def approve(request):
    request_id = request.GET.get("id", "")
    if not request_id.isdigit():
        return JsonResponse({"error": "Invalid id"})

    match _build_leave_service().approve(int(request_id)):
        case ApprovalResult.APPROVED:
            return JsonResponse({"status": "Approved"})
        case ApprovalResult.INSUFFICIENT_BALANCE:
            return JsonResponse({"status": "Refused", "message": "Insufficient balance"})
        case ApprovalResult.NOT_FOUND:
            return JsonResponse({"error": "Leave request not found"})
        case unreachable:
            assert_never(unreachable)
