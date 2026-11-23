from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import role_required
from .forms import ChildForm, CaregiverForm, ZoneForm
from .models import Child, ChildAccess, SafetyZone

User = get_user_model()


def guardian_child(request, child_id):
    """Child that the logged-in guardian actively guards (BR-06)."""
    return get_object_or_404(
        Child, pk=child_id, status="ACTIVE",
        access__user=request.user, access__access_role="GUARDIAN", access__status="ACTIVE")


@role_required("GUARDIAN")
def child_list(request):
    children = Child.objects.filter(
        access__user=request.user, access__access_role="GUARDIAN",
        access__status="ACTIVE", status="ACTIVE")
    return render(request, "safety/child_list.html", {"children": children})


@role_required("GUARDIAN")
def child_create(request):
    form = ChildForm(request.POST or None, guardian=request.user)
    if request.method == "POST" and form.is_valid():
        child = form.save(commit=False)
        child.created_by = request.user
        child.save()
        ChildAccess.objects.create(child=child, user=request.user, access_role="GUARDIAN",
                                   relationship="Guardian", assigned_by=request.user)
        messages.success(request, f"{child.first_name} was added.")
        return redirect("safety:child_detail", child.pk)
    return render(request, "safety/form.html", {"form": form, "title": "Add Child"})


@role_required("GUARDIAN")
def child_detail(request, child_id):
    child = guardian_child(request, child_id)
    return render(request, "safety/child_detail.html", {
        "child": child,
        "zones": child.zones.all(),
        "caregivers": child.access.filter(access_role="CAREGIVER", status="ACTIVE"),
    })


@role_required("GUARDIAN")
def child_edit(request, child_id):
    child = guardian_child(request, child_id)
    form = ChildForm(request.POST or None, instance=child, guardian=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Child updated.")
        return redirect("safety:child_detail", child.pk)
    return render(request, "safety/form.html", {"form": form, "title": "Edit Child"})


@role_required("GUARDIAN")
def child_archive(request, child_id):
    child = guardian_child(request, child_id)
    if request.method == "POST":
        child.status = "ARCHIVED"
        child.save(update_fields=["status"])
        messages.success(request, f"{child.first_name} was archived.")
        return redirect("safety:child_list")
    return render(request, "safety/confirm.html", {"obj": child, "action": "Archive"})


@role_required("GUARDIAN")
def caregiver_add(request, child_id):
    child = guardian_child(request, child_id)
    form = CaregiverForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        user = User.objects.filter(email=email, account_type="CAREGIVER").first()
        active = child.access.filter(access_role="CAREGIVER", status="ACTIVE").count()
        if not user:
            form.add_error("email", "No caregiver account with that email.")
        elif active >= 5:
            form.add_error(None, "A child can have at most 5 caregivers.")  # BR-10
        else:
            acc, created = ChildAccess.objects.get_or_create(
                child=child, user=user,
                defaults={"access_role": "CAREGIVER", "assigned_by": request.user,
                          "relationship": form.cleaned_data["relationship"]})
            if not created:
                if acc.status == "ACTIVE":
                    form.add_error("email", "This caregiver is already assigned.")
                    return render(request, "safety/form.html", {"form": form, "title": "Assign Caregiver"})
                acc.status, acc.revoked_at = "ACTIVE", None
                acc.save(update_fields=["status", "revoked_at"])
            messages.success(request, f"{user.full_name} is now a caregiver for {child.first_name}.")
            return redirect("safety:child_detail", child.pk)
    return render(request, "safety/form.html", {"form": form, "title": "Assign Caregiver"})


@role_required("GUARDIAN")
def caregiver_revoke(request, child_id, access_id):
    child = guardian_child(request, child_id)
    acc = get_object_or_404(ChildAccess, pk=access_id, child=child, access_role="CAREGIVER")
    if request.method == "POST":
        acc.status, acc.revoked_at = "REVOKED", timezone.now()
        acc.save(update_fields=["status", "revoked_at"])
        messages.success(request, "Caregiver access revoked.")
        return redirect("safety:child_detail", child.pk)
    return render(request, "safety/confirm.html", {"obj": acc.user.full_name, "action": "Revoke"})


@role_required("GUARDIAN")
def zone_create(request, child_id):
    child = guardian_child(request, child_id)
    form = ZoneForm(request.POST or None, child=child)
    if request.method == "POST" and form.is_valid():
        zone = form.save(commit=False)
        zone.child, zone.created_by = child, request.user
        zone.save()
        messages.success(request, "Safety zone added.")
        return redirect("safety:child_detail", child.pk)
    return render(request, "safety/form.html", {"form": form, "title": f"Add Zone for {child.first_name}"})


@role_required("GUARDIAN")
def zone_edit(request, child_id, zone_id):
    child = guardian_child(request, child_id)
    zone = get_object_or_404(SafetyZone, pk=zone_id, child=child)
    form = ZoneForm(request.POST or None, instance=zone, child=child)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Zone updated.")
        return redirect("safety:child_detail", child.pk)
    return render(request, "safety/form.html", {"form": form, "title": "Edit Zone"})


@role_required("GUARDIAN")
def zone_delete(request, child_id, zone_id):
    child = guardian_child(request, child_id)
    zone = get_object_or_404(SafetyZone, pk=zone_id, child=child)
    if request.method == "POST":
        zone.is_active = False          # deactivate, never hard delete
        zone.save(update_fields=["is_active"])
        messages.success(request, "Zone deactivated.")
        return redirect("safety:child_detail", child.pk)
    return render(request, "safety/confirm.html", {"obj": zone, "action": "Deactivate"})