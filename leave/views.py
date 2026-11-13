import math
from django.http import JsonResponse
from datetime import date
from .notifications import NotificationService
from .models import Employee, LeaveRequest


def balance(request):
    emp_id = request.GET.get("employeeId")
    e = Employee.objects.filter(id=emp_id).first()
    if e is None:
        return JsonResponse({"error": "Employee not found"})

    if e.contract_type == "CDI":
        days = 25
    elif e.contract_type == "CDD":
        months = math.ceil((date.today() - e.hire_date).days / 30)
        days = months * 2.08
    elif e.contract_type == "Alternance":
        days = 25 + 5
    else:
        days = 0

    return JsonResponse({"employeeId": e.id, "balance": days - e.days_taken})


def approve(request):
    x = request.GET.get("id")
    if x is None or not x.isdigit():
        return JsonResponse({"error": "Invalid id"})

    reqs = [r for r in LeaveRequest.objects.all() if r.id == int(x)]
    req = reqs[0]
    e = Employee.objects.get(id=req.employee_id)

    if e.contract_type == "CDI":
        d = 25
    elif e.contract_type == "CDD":
        m = int((date.today() - e.hire_date).days / 30)
        d = m * 2.08
    elif e.contract_type == "Alternance":
        d = 30
    else:
        d = 0

    if d - e.days_taken < req.working_days:
        req.status = "Refused"
        req.save()
        return JsonResponse({"status": "Refused", "message": "Insufficient balance"})

    req.status = "Approved"
    req.save()
    e.days_taken = e.days_taken + req.working_days
    e.save()

    NotificationService().notify(e, "Votre demande de congés est approuvée.")
    return JsonResponse({"status": "Approved"})
