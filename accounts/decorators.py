from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(role):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.account_type != role:
                messages.error(request, "You don't have access to that page.")
                return redirect("accounts:dashboard")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator