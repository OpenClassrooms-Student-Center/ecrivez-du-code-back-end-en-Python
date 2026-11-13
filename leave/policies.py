from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Protocol

from .models import Employee

DAYS_PER_MONTH = 30
ANNUAL_DAYS = 25
EXAM_PREPARATION_DAYS = 5


class ContractType(StrEnum):
    PERMANENT = "CDI"
    FIXED_TERM = "CDD"
    APPRENTICESHIP = "Alternance"


class LeaveEntitlementPolicy(Protocol):
    """Calcule les droits d’un salarié : toujours un nombre de jours positif ou nul."""

    def compute_entitlement(self, employee: Employee, today: date) -> float: ...


class PermanentContractPolicy:
    def compute_entitlement(self, employee: Employee, today: date) -> float:
        return ANNUAL_DAYS


@dataclass(frozen=True)
class FixedTermContractPolicy:
    days_per_full_month: float = 2.08

    def compute_entitlement(self, employee: Employee, today: date) -> float:
        days_since_hire = (today - employee.hire_date).days
        full_months = days_since_hire // DAYS_PER_MONTH
        return full_months * self.days_per_full_month


class ApprenticeshipPolicy:
    def compute_entitlement(self, employee: Employee, today: date) -> float:
        return ANNUAL_DAYS + EXAM_PREPARATION_DAYS


class LeavePolicyResolver:
    def __init__(self, policies: Mapping[ContractType, LeaveEntitlementPolicy]) -> None:
        self._policies = dict(policies)

    def policy_for(self, contract_type: ContractType) -> LeaveEntitlementPolicy:
        try:
            return self._policies[contract_type]
        except KeyError:
            raise LookupError(f"No leave policy for {contract_type}") from None
