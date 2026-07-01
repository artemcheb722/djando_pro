
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from Book.views import BookListView, BookCreateView, BookDetailView, BookUpdateView, BookDeleteView, cart_add, CartView, cart_remove, clear_cart, CheckoutView
from django.conf.urls.i18n import i18n_patterns
from users.views import register_view, login_view, logout_view
from payments.views import CheckoutSession, CustomerPortalView, WebhookView, CheckoutPaymentPage, checkout_success_page

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns (

    path('books/', BookListView.as_view(), name='book_list'),
    path('books/create/', BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('books/<int:pk>/add_to_cart/', cart_add, name='cart_add'),
    path('cart/remove/<int:book_id>/', cart_remove, name='cart_remove'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('books/<int:pk>/update_book', BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete_book', BookDeleteView.as_view(), name='book_delete'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cart/', CartView.as_view(), name='cart'),
    path('webhook/', WebhookView.as_view(), name='webhook'),
    path('create-checkout-session/', CheckoutSession.as_view(), name='checkout_session'),
    path('customer-portal/', CustomerPortalView.as_view(), name='customer_portal'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout-payment/', CheckoutPaymentPage.as_view(), name='checkout_payment'),
    path('success.html', checkout_success_page, name='checkout_success'),
    prefix_default_language=True,
)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

