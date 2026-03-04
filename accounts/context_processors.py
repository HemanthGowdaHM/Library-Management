# accounts/context_processors.py
# ─────────────────────────────────────────────────────────────────────────────
# Makes {{ user_role }} and role booleans available in EVERY template
# ─────────────────────────────────────────────────────────────────────────────

def user_role(request):
    if request.user.is_authenticated:
        return {
            'user_role':       request.user.role,
            'is_admin':        request.user.is_admin_role,
            'is_librarian':    request.user.is_librarian,
            'is_teacher':      request.user.is_teacher,
            'is_student':      request.user.is_student,
            'can_manage_books': request.user.can_manage_books,
        }
    return {}

# ─────────────────────────────────────────────────────────────────────────────
# ADD THIS TO settings.py → TEMPLATES → OPTIONS → context_processors:
# 'accounts.context_processors.user_role',
# ─────────────────────────────────────────────────────────────────────────────