"""Event URL Configuration."""

from django.urls import path
from . import views


app_name = "event"

urlpatterns = [
    path('create/', views.EventCreateAPIView.as_view(), name='create-event'),
]
