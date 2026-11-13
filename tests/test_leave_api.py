import pytest


@pytest.mark.django_db
def test_approves_request_of_permanent_employee(client, demo_data):
    response = client.get("/api/leave/approve", {"id": 1})

    assert response.status_code == 200
    assert response.json() == {"status": "Approved"}


@pytest.mark.django_db
def test_balance_of_fixed_term_employee_counts_only_full_months(client, demo_data):
    response = client.get("/api/leave/balance", {"employeeId": 4})

    assert response.status_code == 200
    assert response.json()["balance"] == pytest.approx(4.56, abs=0.01)
