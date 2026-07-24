from django.views import View

from .forms import CheckoutForm
from .filters import BookFilter
from .models import Book, Category
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from Book.models import Order, OrderItem, BookReview
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from payments.emails import send_order_confirmation_email
from django.http import HttpResponseNotFound, HttpResponseForbidden
from rest_framework.permissions import IsAuthenticated
from django import forms
from Book.utils import upload_book_image
from django.contrib import messages
from django.db.models import Avg, Count



def render_home_page(request):
    return render(request, 'home_page.html')

class BookListView(ListView):
    model = Book
    template_name = 'book.html'
    context_object_name = 'books'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['filter'] = self.filterset
        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        context['query_params'] = query_params.urlencode()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = BookFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['average_rating'] = self.object.reviews.aggregate(Avg('rating'))['rating__avg']
        return context

    def post(self, request, *args, **kwargs):
        book = self.get_object()

        if not request.user.is_authenticated:
            messages.error(request, "Нужно войти, чтобы оставить отзыв")
            return redirect('login')

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating:
            messages.error(request, "Укажите рейтинг")
            return redirect(request.path)

        BookReview.objects.create(
            book=book,
            user=request.user,
            rating=int(rating),
            comment=comment,
        )

        return redirect(request.path)

class BookCreateView(CreateView):
    model = Book
    template_name = 'book.html'
    fields = ['title', 'author', 'year_of_manufacture', 'price', 'description', 'stock', 'category']
    success_url = reverse_lazy('book_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['image'] = forms.ImageField(required=False)
        return form

    def form_valid(self, form):
        book = form.save(commit=False)

        image_file = form.cleaned_data.get('image')
        if image_file:
            book.image_url = upload_book_image(image_file)

        book.save()
        return redirect(self.success_url)


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


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart = request.session.get('cart', {})

        books_ids = [key for key in cart.keys()]
        books = Book.objects.filter(pk__in=books_ids)
        for itm in books:
            itm.quantity = cart[str(itm.pk)]
        total_price = sum(book.price * cart[str(book.pk)] for book in books)

        return render(request, 'checkout.html',
                      {'cart_items': books, 'total_price': total_price, 'form': CheckoutForm()})

    def post(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('book_list')

        books_ids = cart.keys()
        books = Book.objects.filter(id__in=books_ids)
        total_price = sum(book.price * cart[str(book.pk)] for book in books)

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, 'checkout.html', {
                'cart_items': books,
                'total_price': total_price,
                'form': form,
            })

        order = form.save(commit=False)
        order.user = request.user
        order.total_price = total_price
        order.save()
        send_order_confirmation_email(order)

        for cart_key in cart.keys():
            OrderItem.objects.create(
                order=order,
                book=Book.objects.get(pk=int(cart_key)),
                quantity=cart[cart_key],
            )

        request.session['cart'] = {}
        return redirect('checkout_payment')


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


async def category_detail_view(request, slug):
    request.user = await request.auser()

    try:
        category = await Category.objects.aget(slug=slug)
    except Category.DoesNotExist:
        return HttpResponseNotFound('Категорию не найдено')

    books_qs = Book.objects.filter(category=category).order_by('title')

    total_books = await books_qs.acount()

    books = []
    async for book in books_qs.aiterator():
        books.append(book)

    return render(request, 'category_detail.html', {
        'category': category,
        'books': books,
        'total_books': total_books,
    })


async def order_detail_view(request, pk):
    user = await request.auser()
    request.user = user
    if not user.is_authenticated:
        return redirect('login')

    try:
        order = await Order.objects.select_related('user').aget(pk=pk)
    except Order.DoesNotExist:
        return HttpResponseNotFound('Заказ не найден')

    items = []
    async for item in OrderItem.objects.select_related('book').filter(order=order):
        items.append(item)

    return render(request, 'order_detail.html', {
        'order': order,
        'items': items,
    })


async def user_orders_view(request):
    user = await request.auser()
    request.user = user
    if not user.is_authenticated:
        return redirect('login')

    orders_qs = Order.objects.filter(user=user).order_by('-created_at')

    orders_count = await orders_qs.acount()

    orders = []
    total_spent = 0
    async for order in orders_qs.aiterator():
        orders.append(order)
        total_spent += order.total_price

    return render(request, 'user_orders.html', {
        'orders': orders,
        'orders_count': orders_count,
        'total_spent': total_spent,
    })
