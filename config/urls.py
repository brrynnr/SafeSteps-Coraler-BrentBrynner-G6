from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("safety/", include("safety.urls")),
    path("", lambda r: redirect("accounts:login")),
]