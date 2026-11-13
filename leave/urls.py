from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register("leave-requests", views.LeaveRequestViewSet, basename="leave-request")

urlpatterns = [
    path("employees/<int:employee_id>/balance", views.employee_balance),
    path("", include(router.urls)),
]
