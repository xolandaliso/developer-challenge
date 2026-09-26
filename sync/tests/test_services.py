from unittest.mock import patch

import pytest

from sync.models import Employee, SyncException
from sync.services import run_sync

RAW_RECORDS = [
    {
        "employee_id": "EMP1",
        "first_name": "A",
        "last_name": "One",
        "email": "a.one@company.com",
        "department": "Engineering",
        "location": "CPT",
        "status": "Active",
    },
    {
        # missing employee_id - should be logged, not crash the run
        "employee_id": "",
        "first_name": "Bad",
        "last_name": "Record",
        "email": "bad@company.com",
        "department": "Engineering",
        "location": "Cape Town",
        "status": "Active",
    },
]


@pytest.mark.django_db
@patch("sync.services.fetch_hr_records", return_value=RAW_RECORDS)
def test_run_sync_creates_good_records_and_logs_bad_ones(mock_fetch):
    result = run_sync()

    assert result["fetched"] == 2
    assert result["created"] == 1
    assert result["failed"] == 1
    assert Employee.objects.filter(employee_id="EMP1").exists()
    assert Employee.objects.get(employee_id="EMP1").location == "Cape Town"
    assert SyncException.objects.count() == 1
    assert "employee_id" in SyncException.objects.first().reason


@pytest.mark.django_db
@patch("sync.services.fetch_hr_records", return_value=RAW_RECORDS)
def test_running_sync_twice_does_not_duplicate_employees(mock_fetch):
    run_sync()
    second = run_sync()

    assert Employee.objects.filter(employee_id="EMP1").count() == 1
    # second run updates the already-present employee rather than creating it
    assert second["created"] == 0
    assert second["updated"] == 1


@pytest.mark.django_db
def test_duplicate_employee_in_same_batch_results_in_one_row():
    duplicates = [
        {"employee_id": "EMP9", "first_name": "Sipho", "last_name": "Nkosi",
         "email": "sipho@company.com", "department": "Eng", "location": "JHB",
         "status": "Active"},
        {"employee_id": "EMP9", "first_name": "Sipho", "last_name": "Nkosi",
         "email": "sipho@company.com", "department": "Eng", "location": "Johannesburg",
         "status": "Active"},
    ]
    with patch("sync.services.fetch_hr_records", return_value=duplicates):
        result = run_sync()

    assert Employee.objects.filter(employee_id="EMP9").count() == 1
    assert result["created"] == 1
    assert result["updated"] == 1
