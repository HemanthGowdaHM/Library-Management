from django.contrib import admin
from .models import Book, LibraryDocument


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ('title', 'author', 'isbn', 'quantity', 'added_by', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    list_filter   = ('created_at',)
    ordering      = ('title',)


@admin.register(LibraryDocument)
class LibraryDocumentAdmin(admin.ModelAdmin):
    list_display  = ('title', 'doc_type', 'subject', 'department', 'year', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'subject', 'department')
    list_filter   = ('doc_type', 'department', 'uploaded_at')
    ordering      = ('-uploaded_at',)