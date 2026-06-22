from django.views import View
from .models import Book, Category
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from Book.models import Order, OrderItem
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin

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



class CartView(ListView):
  model = Book
  template_name = 'cart.html'
  context_object_name = 'cart_items'

  def get_queryset(self):
    cart = self.request.session.get('cart', {})
    books_ids = cart.keys()
    books = Book.objects.filter(id__in=books_ids)
    for itm in books:
      itm.quantity = cart[str(itm.pk)]
      itm.item_total_price = itm.price * itm.quantity
    return books

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    total_price = 0
    for book in context['cart_items']:
      total_price += book.item_total_price
    context['total_price'] = total_price
    return context


def cart_view(request):
  cart = request.session.get('cart', {})
  books_ids = Book.objects.filter(id__in=cart.keys())
  cart_items = Book.objects.get(pk__in=books_ids)
  return render(request, 'cart.html', {'cart_items': cart_items, 'cart': cart})





def cart_add(request, pk):
  book_id = str(pk)
  cart = request.session.get('cart', {})
  cart[book_id] = cart.get(book_id, 0) + 1
  request.session['cart'] = cart
  return redirect('book_list')

def cart_remove(request, book_id):
    cart = request.session.get('cart', {})
    if str(book_id) in cart:
        del cart[str(book_id)]
        request.session['cart'] = cart
    return redirect('cart')



def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')