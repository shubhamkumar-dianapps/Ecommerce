from django.urls import path, include

# API versioning - include v1 URLs directly
urlpatterns = [
    path("", include("apps.accounts.v1.urls")),
]
