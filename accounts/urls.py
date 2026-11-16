from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("dashboard/guardian/", views.guardian_dashboard, name="guardian_dashboard"),
    path("dashboard/caregiver/", views.caregiver_dashboard, name="caregiver_dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]