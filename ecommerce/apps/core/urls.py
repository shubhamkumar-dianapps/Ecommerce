"""
URL Configuration for core app testing endpoints.
"""

from django.urls import path
from apps.core.views import TestLoggingView

urlpatterns = [
    path("test-logging/", TestLoggingView.as_view(), name="test-logging"),
]
