from ninja import Schema

class EmployeeOut(Schema):
    '''
        - structure returned by the API for a single employee record.
    '''
    employee_id: str
    first_name: str
    last_name: str
    email: str
    department: str
    location: str
    status: str

class SyncResultOut(Schema):
    '''
        - structure returned by the API for a sync result.
    '''
    fetched: int
    created: int
    updated: int
    failed: int
    errors: list[str]

class ErrorOut(Schema):
    '''
        - structure returned by the API for a single error record.
    '''
    detail: str