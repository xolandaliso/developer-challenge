from django.contrib import admin

from .models import Employee, SyncException


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "first_name", "last_name", "email", "department", "location", "status", "updated_at")
    search_fields = ("employee_id", "first_name", "last_name", "email")
    list_filter = ("status", "department", "location")


@admin.register(SyncException)
class SyncExceptionAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "reason", "occurred_at")
    readonly_fields = ("employee_id", "reason", "raw_payload", "occurred_at")
