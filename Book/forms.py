from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Book
from Book.models import Order

class BookSeachForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category']
        labels = {
            'title': _("Title"),
            'author': _("Author"),
            'category': _("Category"),
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('payment_method', 'post_office_number')
        labels = {
            'payment_method': _("Payment method"),
            'post_office_number': _("Post office number"),
        }