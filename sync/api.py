from ninja import NinjaAPI
from ninja.errors import HttpError

from .models import Employee
from .schema import EmployeeOut, SyncResultOut
from .services import run_sync

api = NinjaAPI(
    title = "Employee Sync API",
    version = "1.0.0",
    description = "API for syncing employee data from the HR system to the payroll system.", 
)

@api.get("/employees/{employee_id}", response = EmployeeOut, summary = "Look up a synced employee")
def get_employee(request, employee_id: str):
    '''
        - look up a synced employee by their employee_id.
    '''
    try:
        employee = Employee.objects.get(employee_id = employee_id)
    except Employee.DoesNotExist:
        raise HttpError(404, f"Employee with ID {employee_id} not found.")
    
    return EmployeeOut(
        employee_id = employee.employee_id,
        first_name = employee.first_name,
        last_name = employee.last_name,
        email = employee.email,
        department = employee.department,
        location = employee.location,
        status = employee.status,
    )
@api.post("/sync", response = SyncResultOut, summary = "Trigger a sync run")
def sync_employees(request):
    '''
        - trigger a sync run.
    '''
    return run_sync()