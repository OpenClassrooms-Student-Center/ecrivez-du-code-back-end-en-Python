import pytest


@pytest.mark.django_db
def test_approves_request_of_permanent_employee(client, demo_data):
    response = client.post("/api/leave-requests/1/approval")

    assert response.status_code == 200
    assert response.json()["status"] == "Approved"


@pytest.mark.django_db
def test_balance_of_fixed_term_employee_counts_only_full_months(client, demo_data):
    response = client.get("/api/employees/4/balance")

    assert response.status_code == 200
    assert response.json()["balance"] == pytest.approx(4.56, abs=0.01)


@pytest.mark.django_db
def test_balance_response_keeps_its_contract(client, demo_data):
    response = client.get("/api/employees/4/balance")

    assert set(response.json()) == {"employeeId", "balance"}


@pytest.mark.django_db
def test_approving_a_request_twice_returns_conflict(client, demo_data):
    client.post("/api/leave-requests/7/approval")
    response = client.post("/api/leave-requests/7/approval")

    assert response.status_code == 409


@pytest.mark.django_db
def test_creating_a_request_ending_before_it_starts_returns_bad_request(
    client, demo_data
):
    response = client.post(
        "/api/leave-requests",
        {"employeeId": 4, "startDate": "2026-07-10", "endDate": "2026-07-06"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "endDate" in response.json()


@pytest.mark.django_db
def test_balance_of_intern_is_zero_before_the_internship_starts(client, demo_data):
    response = client.get("/api/employees/6/balance")

    assert response.status_code == 200
    assert response.json()["balance"] == 0
