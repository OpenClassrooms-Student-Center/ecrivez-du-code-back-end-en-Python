from datetime import date

import pytest

from leave.models import Employee
from leave.policies import FixedTermContractPolicy


def test_fixed_term_policy_counts_only_full_months():
    policy = FixedTermContractPolicy()
    employee = Employee(hire_date=date(2026, 3, 15))

    entitlement = policy.compute_entitlement(employee, date(2026, 10, 20))

    assert entitlement == pytest.approx(14.56)
