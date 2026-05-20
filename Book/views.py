from django.shortcuts import render
from django.db.models import Q
from .models import Book
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

class BookListView(ListView):
  model = Book
  template_name = 'book.html'
  context_object_name = 'books'
  paginate_by = 15


class BookDetailView(DetailView):
  model = Book
  template_name = 'book_detail.html'
  context_object_name = 'book'


class BookCreateView(CreateView):
  model = Book
  template_name = 'book_create_form.html'
  fields = ['title', 'author', 'year_of_manufacture', 'price', 'description', 'stock', 'category']
  success_url = reverse_lazy('book_list')

class BookUpdateView(UpdateView):
  model = Book
  template_name = 'book_update_form.html'
  fields = ['title', 'author', 'year_of_manufacture', 'price', 'description', 'stock', 'category']
  success_url = reverse_lazy('book_list')


class BookDeleteView(DeleteView):
  model = Book
  template_name = 'book_confirm_delete.html'
  success_url = reverse_lazy('book_list')


