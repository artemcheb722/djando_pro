
from .models import Book, Category
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

class BookListView(ListView):
  model = Book
  template_name = 'book.html'
  context_object_name = 'books'
  paginate_by = 15

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['categories'] = Category.objects.all()
    return context

  def get_queryset(self):
    queryset = super().get_queryset()
    user_search_query = self.request.GET.get("q", None)
    if user_search_query:
      queryset = queryset.filter(title__icontains=user_search_query)
    return queryset



class BookDetailView(DetailView):
  model = Book
  template_name = 'book_detail.html'
  context_object_name = 'book'





class BookCreateView(CreateView):
  model = Book
  template_name = 'book.html'
  fields = ['title', 'author', 'year_of_manufacture', 'price', 'description', 'stock', 'category']
  success_url = reverse_lazy('book_list')



class BookUpdateView(UpdateView):
  model = Book
  template_name = 'book.html'
  fields = ['title', 'author', 'year_of_manufacture', 'price', 'description', 'stock', 'category']
  success_url = reverse_lazy('book_list')


class BookDeleteView(DeleteView):
  model = Book
  template_name = 'book_confirm_delete.html'
  success_url = reverse_lazy('book_list')


