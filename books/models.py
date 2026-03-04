from django.db import models
from django.conf import settings


class Book(models.Model):
    """Physical or digital book in the library catalogue."""

    title          = models.CharField(max_length=200, db_index=True)
    author         = models.CharField(max_length=200, db_index=True)
    isbn           = models.CharField(max_length=13, unique=True, db_index=True)
    published_date = models.DateField()
    quantity       = models.PositiveIntegerField(default=1)
    description    = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    added_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='books_added',
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} — {self.author}"


class LibraryDocument(models.Model):
    """PDFs, question papers, notes and study material."""

    class DocType(models.TextChoices):
        PDF           = 'PDF',           'PDF / E-Book'
        QUESTION_CURR = 'QUESTION_CURR', 'Question Paper (Current Year)'
        QUESTION_PREV = 'QUESTION_PREV', 'Question Paper (Previous Year)'
        NOTES         = 'NOTES',         'Notes / Study Material'
        OTHER         = 'OTHER',         'Other'

    title       = models.CharField(max_length=200)
    doc_type    = models.CharField(max_length=20, choices=DocType.choices, default=DocType.PDF)
    subject     = models.CharField(max_length=100, blank=True, help_text="Subject / Course name")
    department  = models.CharField(max_length=100, blank=True)
    year        = models.PositiveIntegerField(null=True, blank=True, help_text="Exam year (for question papers)")
    description = models.TextField(blank=True)
    file        = models.FileField(upload_to='library_docs/%Y/%m/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documents_uploaded',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public   = models.BooleanField(default=True, help_text="Visible to all approved members")

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_doc_type_display()} — {self.title}"

    @property
    def file_extension(self):
        import os
        _, ext = os.path.splitext(self.file.name)
        return ext.lower()

    @property
    def is_pdf(self):
        return self.file_extension == '.pdf'