import pytest
from django.test import Client

from sync.models import Employee


@pytest.mark.django_db
def test_get_unknown_employee_returns_404():
    client = Client()
    resp = client.get("/api/employees/DOES-NOT-EXIST")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_get_known_employee_returns_record():
    Employee.objects.create(
        employee_id="EMP1", first_name="A", last_name="One",
        email="a.one@company.com", department="Engineering",
        location="Cape Town", status="Active",
    )
    client = Client()
    resp = client.get("/api/employees/EMP1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["employee_id"] == "EMP1"
    assert body["email"] == "a.one@company.com"
