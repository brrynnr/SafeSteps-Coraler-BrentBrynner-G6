from django.urls import path
from . import views

app_name = "safety"
urlpatterns = [
    path("children/", views.child_list, name="child_list"),
    path("children/add/", views.child_create, name="child_create"),
    path("children/<int:child_id>/", views.child_detail, name="child_detail"),
    path("children/<int:child_id>/edit/", views.child_edit, name="child_edit"),
    path("children/<int:child_id>/archive/", views.child_archive, name="child_archive"),
    path("children/<int:child_id>/caregivers/add/", views.caregiver_add, name="caregiver_add"),
    path("children/<int:child_id>/caregivers/<int:access_id>/revoke/", views.caregiver_revoke, name="caregiver_revoke"),
    path("children/<int:child_id>/zones/add/", views.zone_create, name="zone_create"),
    path("children/<int:child_id>/zones/<int:zone_id>/edit/", views.zone_edit, name="zone_edit"),
    path("children/<int:child_id>/zones/<int:zone_id>/deactivate/", views.zone_delete, name="zone_delete"),
]