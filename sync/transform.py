'''
    - validate and transform raw HR-system payloads into the shape the
    downstream (payroll) store expects.

'''


class RecordInvalid(Exception):
    '''
        - custom exception - raised when a raw HR record cannot be safely transformed.
    '''


# loc codes the source system sometimes sends instead of the full name.
LOCATION_MAP = {
    "CPT": "Cape Town",
    "JHB": "Johannesburg",
    "DBN": "Durban",
    "PTA": "Pretoria",
}

# depts spellings/variants we've seen from the source system, normalised
# to a single form. anything not listed here is passed through
# (after whitespace/case tidy-up) rather than rejected — we don't want to
# fail a whole record just because a department isn't in our map.
DEPARTMENT_MAP = {
    "data and ai": "Data & AI",
    "data & ai": "Data & AI",
}

VALID_STATUSES = {"Active", "Inactive", "On Leave"}


def normalize_text(value) -> str:
    if not value:
        return ""
    return " ".join(str(value).strip().split())


def normalize_location(value: str) -> str:
    value = normalize_text(value)
    return LOCATION_MAP.get(value.upper(), value)


def normalize_department(value: str) -> str:
    value = normalize_text(value)
    return DEPARTMENT_MAP.get(value.lower(), value)


def validate_and_transform(raw) -> dict:
    '''
        - validate a single raw HR record and transform it into the payload the
        downstream Employee table expects.

        - raises RecordInvalid for anything that
        cannot be safely processed. 
    '''
    if not isinstance(raw, dict):
        raise RecordInvalid("record is not a JSON object")

    employee_id = normalize_text(raw.get("employee_id"))
    email = normalize_text(raw.get("email"))

    if not employee_id and not email:
        raise RecordInvalid(
            "missing employee_id and email - cannot identify the employee"
        )
    if not employee_id:
        raise RecordInvalid("missing employee_id")

    first_name = normalize_text(raw.get("first_name"))
    last_name = normalize_text(raw.get("last_name"))
    if not first_name or not last_name:
        raise RecordInvalid("missing first_name or last_name")

    if not email or "@" not in email:
        raise RecordInvalid("missing or invalid email")
    email = email.lower()

    status = normalize_text(raw.get("status"))
    if status not in VALID_STATUSES:
        raise RecordInvalid(f"invalid status: '{status or 'blank'}'")

    department = normalize_department(raw.get("department")) or "Unknown"
    location = normalize_location(raw.get("location")) or "Unknown"

    return {
        "employee_id": employee_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "department": department,
        "location": location,
        "status": status,
    }
