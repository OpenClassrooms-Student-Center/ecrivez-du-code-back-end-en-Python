from django.db import models


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contract_type = models.CharField(max_length=20)
    hire_date = models.DateField()
    days_taken = models.FloatField(default=0)


class LeaveRequest(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_requests"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    working_days = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="Pending")
