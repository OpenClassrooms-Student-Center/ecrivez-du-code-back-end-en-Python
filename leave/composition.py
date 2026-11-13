from django.conf import settings

from .notifications import NotificationService
from .policies import (
    ApprenticeshipPolicy,
    ContractType,
    FixedTermContractPolicy,
    InternshipPolicy,
    LeavePolicyResolver,
    PermanentContractPolicy,
)
from .services import LeaveService


def build_policy_resolver() -> LeavePolicyResolver:
    return LeavePolicyResolver({
        ContractType.PERMANENT: PermanentContractPolicy(),
        ContractType.FIXED_TERM: FixedTermContractPolicy(
            days_per_full_month=settings.HAMAC_FIXED_TERM_DAYS_PER_FULL_MONTH,
        ),
        ContractType.APPRENTICESHIP: ApprenticeshipPolicy(),
        ContractType.INTERNSHIP: InternshipPolicy(),
    })


def build_leave_service() -> LeaveService:
    return LeaveService(build_policy_resolver(), NotificationService())
