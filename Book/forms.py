from django import forms
from .models import Book

class BookSeachForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category']