import pytest

from sync.transform import RecordInvalid, validate_and_transform


def test_valid_record_is_normalised():
    raw = {
        "employee_id": "EMP1",
        "first_name": " Amira ",
        "last_name": "Khan",
        "email": "Amira.Khan@Company.COM",
        "department": "Data and AI",
        "location": "CPT",
        "status": "Active",
    }
    clean = validate_and_transform(raw)
    assert clean["email"] == "amira.khan@company.com"
    assert clean["department"] == "Data & AI"
    assert clean["location"] == "Cape Town"
    assert clean["first_name"] == "Amira"


def test_missing_employee_id_raises():
    raw = {"employee_id": "", "first_name": "A", "last_name": "B",
           "email": "a@b.com", "status": "Active"}
    with pytest.raises(RecordInvalid):
        validate_and_transform(raw)


def test_missing_employee_id_and_email_is_unrecoverable():
    with pytest.raises(RecordInvalid, match="cannot identify"):
        validate_and_transform({"first_name": "A", "last_name": "B"})


def test_invalid_status_raises():
    raw = {"employee_id": "EMP2", "first_name": "A", "last_name": "B",
           "email": "a@b.com", "status": "On Secondment"}
    with pytest.raises(RecordInvalid, match="invalid status"):
        validate_and_transform(raw)


def test_non_dict_record_raises():
    with pytest.raises(RecordInvalid, match="not a JSON object"):
        validate_and_transform("this-is-not-a-record")


def test_unmapped_location_passes_through_unchanged():
    raw = {"employee_id": "EMP3", "first_name": "A", "last_name": "B",
           "email": "a@b.com", "status": "Active", "location": "London"}
    clean = validate_and_transform(raw)
    assert clean["location"] == "London"
