from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Usage:
        @role_required('ADMIN', 'LIBRARIAN')
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, "You don't have permission to access this page.")
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def approved_required(view_func):
    """Blocks unapproved members from accessing views."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_approved and not request.user.is_superuser:
            messages.warning(request, "Your account is pending approval by the librarian.")
            return redirect('accounts:pending_approval')
        return view_func(request, *args, **kwargs)
    return _wrapped


# Shortcut aliases
admin_required = role_required('ADMIN')
librarian_required = role_required('ADMIN', 'LIBRARIAN')
staff_required = role_required('ADMIN', 'LIBRARIAN')