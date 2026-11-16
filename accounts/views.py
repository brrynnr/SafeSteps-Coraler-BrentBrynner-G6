from django.views.decorators.cache import never_cache
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import User

MAX_FAILS, LOCK_MIN = 5, 15


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created! Please log in.")
        return redirect("accounts:login")
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        password = form.cleaned_data["password"]
        account = User.objects.filter(email=email).first()

        if account and account.locked_until and account.locked_until > timezone.now():
            messages.error(request, "Account locked. Try again in 15 minutes.")
        else:
            user = authenticate(request, username=email, password=password)
            if user:
                user.failed_login_count = 0
                user.locked_until = None
                user.save(update_fields=["failed_login_count", "locked_until"])
                login(request, user)
                messages.success(request, f"Welcome back, {user.full_name}!")
                return redirect(request.GET.get("next") or "accounts:dashboard")
            if account:
                account.failed_login_count += 1
                if account.failed_login_count >= MAX_FAILS:
                    account.locked_until = timezone.now() + timedelta(minutes=LOCK_MIN)
                    account.failed_login_count = 0
                account.save(update_fields=["failed_login_count", "locked_until"])
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
@never_cache
def dashboard_redirect(request):
    if request.user.account_type == User.AccountType.GUARDIAN:
        return redirect("accounts:guardian_dashboard")
    return redirect("accounts:caregiver_dashboard")


@role_required("GUARDIAN")
@never_cache
def guardian_dashboard(request):
    return render(request, "accounts/guardian_dashboard.html")


@role_required("CAREGIVER")
@never_cache
def caregiver_dashboard(request):
    return render(request, "accounts/caregiver_dashboard.html")


@login_required
@never_cache
def profile_view(request):
    return render(request, "accounts/profile.html", {"profile": request.user})


@login_required
@never_cache
def profile_edit(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile_edit.html", {"form": form})