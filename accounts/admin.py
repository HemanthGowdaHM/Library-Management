from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BorrowRecord


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_approved', 'date_joined')
    list_filter = ('role', 'is_approved', 'department')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'student_id')
    ordering = ('-date_joined',)
    list_editable = ('is_approved', 'role')

    fieldsets = UserAdmin.fieldsets + (
        ('Library Info', {
            'fields': ('role', 'phone_number', 'department', 'student_id', 'profile_picture', 'is_approved'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Library Info', {
            'fields': ('role', 'phone_number', 'department', 'student_id', 'is_approved'),
        }),
    )


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'borrowed_date', 'due_date', 'returned_date', 'fine_amount')
    list_filter = ('status', 'borrowed_date')
    search_fields = ('user__username', 'book__title')
    date_hierarchy = 'borrowed_date'
