from django.urls import path

from . import views

urlpatterns = [
    path("balance", views.balance),
    path("approve", views.approve),
]
