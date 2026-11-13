from django.urls import include, path

urlpatterns = [
    path("api/leave/", include("leave.urls")),
]
