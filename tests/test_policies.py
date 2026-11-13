from datetime import date

import pytest

from leave.models import Employee
from leave.policies import FixedTermContractPolicy, InternshipPolicy


def test_fixed_term_policy_counts_only_full_months():
    policy = FixedTermContractPolicy()
    employee = Employee(hire_date=date(2026, 3, 15))

    entitlement = policy.compute_entitlement(employee, date(2026, 10, 20))

    assert entitlement == pytest.approx(14.56)


def test_fixed_term_policy_rejects_non_positive_rate():
    with pytest.raises(ValueError):
        FixedTermContractPolicy(days_per_full_month=-1)


def test_internship_policy_counts_only_full_months():
    policy = InternshipPolicy()
    employee = Employee(hire_date=date(2026, 3, 15))

    entitlement = policy.compute_entitlement(employee, date(2026, 10, 20))

    assert entitlement == 14


def test_internship_policy_gives_no_days_before_the_internship_starts():
    policy = InternshipPolicy()
    employee = Employee(hire_date=date(2026, 10, 27))

    entitlement = policy.compute_entitlement(employee, date(2026, 10, 20))

    assert entitlement == 0
