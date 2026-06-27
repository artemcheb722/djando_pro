from django import forms
from .models import Book
from Book.models import Order

class BookSeachForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category']

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('payment_method', 'post_office_number')

