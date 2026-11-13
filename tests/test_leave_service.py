import pytest

from leave.composition import build_leave_service, build_policy_resolver
from leave.models import Employee
from leave.services import ApprovalResult, LeaveService


class FakeNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[Employee, str]] = []

    def notify(self, employee: Employee, message: str) -> None:
        self.sent.append((employee, message))


def test_composition_builds_leave_service():
    assert isinstance(build_leave_service(), LeaveService)


@pytest.mark.django_db
def test_approval_notifies_employee(demo_data):
    notifier = FakeNotifier()
    service = LeaveService(build_policy_resolver(), notifier)

    result = service.approve(1)

    assert result is ApprovalResult.APPROVED
    assert [message for _, message in notifier.sent] == [
        "Votre demande de congés est approuvée."
    ]
