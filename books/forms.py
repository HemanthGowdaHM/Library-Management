from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'published_date':forms.DateInput(attrs={'type':'date'}),
        }