from django import forms
from django.utils import timezone
from .models import Book, LibraryDocument


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'quantity', 'description']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'description':    forms.Textarea(attrs={'rows': 3}),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').replace('-', '').strip()
        if not isbn:
            raise forms.ValidationError('ISBN is required.')
        if not isbn.isdigit():
            raise forms.ValidationError('ISBN should contain only digits.')
        if len(isbn) not in (10, 13):
            raise forms.ValidationError('ISBN must be either 10 or 13 digits long.')
        qs = Book.objects.filter(isbn__iexact=isbn)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A book with that ISBN already exists.')
        return isbn

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None:
            return qty
        if qty < 0:
            raise forms.ValidationError('Quantity cannot be negative.')
        return qty

    def clean_published_date(self):
        pd = self.cleaned_data.get('published_date')
        if pd and pd > timezone.now().date():
            raise forms.ValidationError('Published date cannot be in the future.')
        return pd


class LibraryDocumentForm(forms.ModelForm):
    class Meta:
        model  = LibraryDocument
        fields = ['title', 'doc_type', 'subject', 'department', 'year', 'description', 'file', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        doc_type = cleaned_data.get('doc_type')
        year = cleaned_data.get('year')
        if doc_type in (
            LibraryDocument.DocType.QUESTION_CURR,
            LibraryDocument.DocType.QUESTION_PREV,
        ) and not year:
            self.add_error('year', 'Year is required for question papers.')
        return cleaned_data

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            allowed = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.png']
            import os
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in allowed:
                raise forms.ValidationError(
                    f"File type '{ext}' not allowed. Allowed: {', '.join(allowed)}"
                )
            if f.size > 50 * 1024 * 1024:   # 50 MB limit
                raise forms.ValidationError("File too large. Maximum size is 50 MB.")
        return f