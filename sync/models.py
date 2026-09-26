from django.db import models


class Employee(models.Model):
    '''
        - the consolidated, downstream ("payroll") employee record.

        - 'employee_id' is the key we upsert on, making a re-run possible
           i.e. the same source record always lands on the same row.
    '''

    class Status(models.TextChoices):
        ACTIVE = "Active", "Active"
        INACTIVE = "Inactive", "Inactive"
        ON_LEAVE = "On Leave", "On Leave"

    employee_id = models.CharField(max_length = 32, unique = True, db_index = True)
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    email = models.EmailField()
    department = models.CharField(max_length = 100)
    location = models.CharField(max_length = 100)
    status = models.CharField(max_length = 20, choices = Status.choices)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ["employee_id"]

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.first_name} {self.last_name}"


class SyncException(models.Model):
    '''
        - an error table
    '''

    employee_id = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    reason = models.CharField(max_length=255)
    raw_payload = models.JSONField()
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self) -> str:
        return f"{self.employee_id or 'unknown'}: {self.reason}"
