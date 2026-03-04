from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone


import json
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import CustomUser, BorrowRecord
from .decorators import approved_required, staff_required
from books.models import Book



from .models import CustomUser, BorrowRecord
from .forms import (
    RegisterForm, CustomLoginForm,
    AdminCreateUserForm, ProfileUpdateForm, AdminApproveUserForm,
)
from .decorators import approved_required, staff_required, admin_required


# ─────────────────────────────────────────────
#  PUBLIC VIEWS
# ─────────────────────────────────────────────

def register_view(request):
    """Any visitor can register; account awaits admin approval."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False        # requires admin approval
            user.save()
            messages.success(request, "Account created! Please wait for admin approval.")
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect(request.GET.get('next', 'accounts:dashboard'))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


def pending_approval_view(request):
    return render(request, 'accounts/pending_approval.html')


# ─────────────────────────────────────────────
#  MEMBER VIEWS (login + approved)
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
#  UPDATED DASHBOARD VIEW (with activity search)
# ─────────────────────────────────────────────

@login_required
@approved_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}

    if user.can_manage_books:
        context['total_users']   = CustomUser.objects.count()
        context['pending_users'] = CustomUser.objects.filter(is_approved=False).count()
        context['active_borrows'] = BorrowRecord.objects.filter(
            status__in=['BORROWED', 'OVERDUE']
        ).count()

        # Activity search / filter
        activity_q      = request.GET.get('activity_q', '').strip()
        activity_status = request.GET.get('activity_status', '')

        records = BorrowRecord.objects.select_related('user', 'book').order_by('-borrowed_date')

        if activity_q:
            records = records.filter(
                Q(user__first_name__icontains=activity_q) |
                Q(user__last_name__icontains=activity_q)  |
                Q(user__username__icontains=activity_q)   |
                Q(user__student_id__icontains=activity_q) |
                Q(book__title__icontains=activity_q)
            )
        if activity_status:
            records = records.filter(status=activity_status)

        context['recent_borrows']   = records[:20]
        context['activity_q']       = activity_q
        context['activity_status']  = activity_status
        context['status_choices']   = BorrowRecord.Status.choices

    else:
        my_records = BorrowRecord.objects.filter(user=user).select_related('book')
        context['my_borrows']  = my_records.filter(status='BORROWED')
        context['my_overdue']  = my_records.filter(status='OVERDUE')
        context['my_history']  = my_records[:10]
        context['total_fine']  = sum(r.calculate_fine() for r in context['my_borrows'])

    return render(request, 'accounts/dashboard.html', context)



@login_required
@approved_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {
    'form': form,
    'account_info': [
        ('Username', request.user.username),
        ('Student ID', request.user.student_id or '—'),
        ('Phone', request.user.phone_number or '—'),
        ('Member Since', request.user.date_joined.strftime('%d %B %Y')),
        ]
    })


@login_required
@approved_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
@approved_required
def my_borrowing_history(request):
    records = BorrowRecord.objects.filter(
        user=request.user
    ).select_related('book').order_by('-borrowed_date')

    # Mark overdue
    today = timezone.now().date()
    for r in records:
        if r.status == 'BORROWED' and r.due_date < today:
            r.status = 'OVERDUE'
            r.save(update_fields=['status'])

    return render(request, 'accounts/borrow_history.html', {'records': records})


# ─────────────────────────────────────────────
#  ADMIN / LIBRARIAN VIEWS
# ─────────────────────────────────────────────

@login_required
@staff_required
def manage_users_view(request):
    """List all users with filters."""
    role_filter = request.GET.get('role', '')
    approved_filter = request.GET.get('approved', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if approved_filter == 'pending':
        users = users.filter(is_approved=False)
    elif approved_filter == 'approved':
        users = users.filter(is_approved=True)
    context = {
        'users': users,
        'roles': CustomUser.Role.choices,
        'role_filter': role_filter,
        'approved_filter': approved_filter,
    }
    return render(request, 'accounts/manage_users.html', context)


@login_required
@staff_required
def create_user_view(request):
    """Admin/Librarian creates a new user directly."""
    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect('accounts:manage_users')
    else:
        form = AdminCreateUserForm()
    return render(request, 'accounts/create_user.html', {'form': form})


@login_required
@staff_required
def approve_user_view(request, user_id):
    """Approve or update a pending user."""
    member = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = AdminApproveUserForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            action = "approved" if member.is_approved else "updated"
            messages.success(request, f"User {member.username} {action}.")
            return redirect('accounts:manage_users')
    else:
        form = AdminApproveUserForm(instance=member)
    return render(request, 'accounts/approve_user.html', {'form': form, 'member': member})


@login_required
@admin_required
def delete_user_view(request, user_id):
    member = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        member.delete()
        messages.success(request, "User deleted.")
        return redirect('accounts:manage_users')
    return render(request, 'accounts/delete_user.html', {'member': member})


@login_required
@staff_required
def user_borrow_history(request, user_id):
    """View borrow history of any specific user."""
    member = get_object_or_404(CustomUser, pk=user_id)
    records = BorrowRecord.objects.filter(
        user=member
    ).select_related('book').order_by('-borrowed_date')
    return render(request, 'accounts/borrow_history.html', {
        'records': records,
        'member': member,
    })

# ─────────────────────────────────────────────
#  UPDATED ISSUE BOOK VIEW
# ─────────────────────────────────────────────

@login_required
@staff_required
def issue_book_view(request):
    import datetime
    if request.method == 'POST':
        user_id  = request.POST.get('user_id')
        book_id  = request.POST.get('book_id')
        due_days = int(request.POST.get('due_days', 14))

        member = get_object_or_404(CustomUser, pk=user_id, is_approved=True)
        book   = get_object_or_404(Book, pk=book_id)

        if book.quantity < 1:
            messages.error(request, f"No copies of '{book.title}' are currently available.")
        else:
            due_date = timezone.now().date() + datetime.timedelta(days=due_days)
            BorrowRecord.objects.create(
                user=member, book=book,
                due_date=due_date, status='BORROWED',
            )
            book.quantity -= 1
            book.save(update_fields=['quantity'])
            messages.success(
                request,
                f"✓ '{book.title}' issued to {member.get_full_name() or member.username}. Due: {due_date}"
            )
            return redirect('accounts:dashboard')

    return render(request, 'accounts/issue_book.html')

# Replace the return_book_view function in accounts/views.py with this:

@login_required
@staff_required
def return_book_view(request, record_id):
    """Librarian marks a book as returned."""
    record = get_object_or_404(BorrowRecord, pk=record_id)

    if request.method == 'POST':
        record.returned_date = timezone.now()
        record.fine_amount = record.calculate_fine()
        record.status = BorrowRecord.Status.RETURNED
        record.save()
        record.book.quantity += 1
        record.book.save(update_fields=['quantity'])
        if record.fine_amount:
            messages.success(request, f"Book returned. Fine collected: ₹{record.fine_amount}")
        else:
            messages.success(request, "Book returned successfully.")
        return redirect('accounts:dashboard')

    # GET request — build context for template
    loan_days = (record.due_date - record.borrowed_date.date()).days

    return_info = [
        ('Borrowed by',  record.user.get_full_name() or record.user.username),
        ('Borrowed on',  record.borrowed_date.strftime('%d %b %Y')),
        ('Due date',     str(record.due_date)),
        ('Loan period',  f"{loan_days} day{'s' if loan_days != 1 else ''}"),
    ]

    return render(request, 'accounts/return_book.html', {
        'record': record,
        'return_info': return_info,
    })


def forgot_password_view(request):
    """Account recovery by phone number or username + email."""
    if request.method == 'POST':
        method = request.POST.get('method')

        if method == 'phone':
            phone = request.POST.get('phone_number', '').strip()
            try:
                user = CustomUser.objects.get(phone_number=phone)
                # TODO: Integrate SMS provider (e.g. Twilio / MSG91)
                # send_sms(user.phone_number, reset_link)
            except CustomUser.DoesNotExist:
                pass  # Don't reveal whether number exists
            messages.success(request,
                "If that phone number is registered, you'll receive an SMS shortly.")

        elif method == 'username':
            username = request.POST.get('username_recover', '').strip()
            email = request.POST.get('email', '').strip()
            try:
                user = CustomUser.objects.get(username=username, email__iexact=email)
                from django.contrib.auth.tokens import default_token_generator
                from django.utils.http import urlsafe_base64_encode
                from django.utils.encoding import force_bytes
                from django.core.mail import send_mail

                uid   = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(f'/accounts/reset/{uid}/{token}/')

                send_mail(
                    subject='College Library — Password Reset',
                    message=f'Click the link below to reset your password:\n\n{reset_url}\n\nIf you did not request this, ignore this email.',
                    from_email='library@college.edu',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except CustomUser.DoesNotExist:
                pass
            messages.success(request,
                "If that username and email match, a reset link has been sent to your inbox.")

    return redirect('accounts:login')


def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)





# ─────────────────────────────────────────────
#  AJAX SEARCH ENDPOINTS
# ─────────────────────────────────────────────

@login_required
@staff_required
def search_members_ajax(request):
    """Returns JSON list of members matching name or student ID."""
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})

    members = CustomUser.objects.filter(
        is_approved=True
    ).exclude(role__in=['ADMIN', 'LIBRARIAN']).filter(
        Q(first_name__icontains=q) |
        Q(last_name__icontains=q)  |
        Q(username__icontains=q)   |
        Q(student_id__icontains=q)
    )[:10]

    results = [
        {
            'id':         m.pk,
            'name':       m.get_full_name() or m.username,
            'username':   m.username,
            'student_id': m.student_id or '—',
            'role':       m.get_role_display(),
            'dept':       m.department or '',
            'initial':    (m.first_name[:1] or m.username[:1]).upper(),
        }
        for m in members
    ]
    return JsonResponse({'results': results})


@login_required
@staff_required
def search_books_ajax(request):
    """Returns JSON list of available books matching title/author."""
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})

    books = Book.objects.filter(
        Q(title__icontains=q) | Q(author__icontains=q)
    ).filter(quantity__gt=0)[:10]

    results = [
        {
            'id':     b.pk,
            'title':  b.title,
            'author': b.author,
            'qty':    b.quantity,
            'isbn':   b.isbn,
        }
        for b in books
    ]
    return JsonResponse({'results': results})
