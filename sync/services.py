'''
    orchestrates a sync run: fetch from the HR REST API, validate/transform each
    record, and upsert the good ones into the downstream store — logging the bad
    ones instead of letting them blow up the whole run.
'''
import requests
from django.conf import settings
from django.db import transaction

from .models import Employee, SyncException
from .transform import RecordInvalid, validate_and_transform


def fetch_hr_records() -> list:
    '''
        - consume the upstream HR REST API (System A) and return the raw list.
    '''
    response = requests.get(settings.HR_API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError("HR API did not return a JSON array of records")
    return data


def log_failure(raw, reason: str) -> None:
    employee_id = None
    payload = {"value": raw}
    if isinstance(raw, dict):
        payload = raw
        employee_id = (raw.get("employee_id") or "").strip() or None

    SyncException.objects.create(
        employee_id=employee_id,
        reason=reason,
        raw_payload=payload,
    )


def run_sync() -> dict:
    '''
        fetch + validate + upsert every record from the HR API.

        upserting on 'employee_id' - for a safe re-run.
    '''
    raw_records = fetch_hr_records()

    created = updated = failed = 0
    errors: list[str] = []

    for raw in raw_records:
        try:
            clean = validate_and_transform(raw)
        except RecordInvalid as exc:
            failed += 1
            errors.append(str(exc))
            log_failure(raw, str(exc))
            continue

        with transaction.atomic():
            _obj, was_created = Employee.objects.update_or_create(
                employee_id=clean["employee_id"],
                defaults={k: v for k, v in clean.items() if k != "employee_id"},
            )

        if was_created:
            created += 1
        else:
            updated += 1

    return {
        "fetched": len(raw_records),
        "created": created,
        "updated": updated,
        "failed": failed,
        "errors": errors,
    }
