from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended User model with library-specific roles."""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        LIBRARIAN = 'LIBRARIAN', 'Librarian'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)   # e.g. "Computer Science"
    student_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)            # Admin must approve new members
    date_of_joining = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ---------- handy role helpers ----------
    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_librarian(self):
        return self.role == self.Role.LIBRARIAN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def can_manage_books(self):
        """Admins and Librarians can add/edit/delete books."""
        return self.role in (self.Role.ADMIN, self.Role.LIBRARIAN)


class BorrowRecord(models.Model):
    """Tracks every borrow/return event."""

    class Status(models.TextChoices):
        BORROWED = 'BORROWED', 'Borrowed'
        RETURNED = 'RETURNED', 'Returned'
        OVERDUE = 'OVERDUE', 'Overdue'
        RESERVED = 'RESERVED', 'Reserved'

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='borrow_records',
    )
    book = models.ForeignKey(
        'books.Book',                       # reference existing Book model
        on_delete=models.CASCADE,
        related_name='borrow_records',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BORROWED,
    )
    borrowed_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-borrowed_date']

    def __str__(self):
        return f"{self.user.username} → {self.book.title} [{self.status}]"

    def calculate_fine(self):
        """₹5 per day after due date."""
        from django.utils import timezone
        import datetime
        if self.status == self.Status.RETURNED:
            return self.fine_amount
        today = timezone.now().date()
        if today > self.due_date:
            overdue_days = (today - self.due_date).days
            return overdue_days * 5
        return 0
