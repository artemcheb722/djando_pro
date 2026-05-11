from django.shortcuts import render
from django.db.models import Q
from .models import Book


def books(request):
  result = Book.objects.all()
  return render(request, 'book.html')

