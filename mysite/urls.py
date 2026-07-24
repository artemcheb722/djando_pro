from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from Book.views import (BookListView,
                        BookCreateView,
                        BookDetailView,
                        BookUpdateView,
                        BookDeleteView,
                        cart_add,
                        CartView,
                        cart_remove,
                        clear_cart,
                        CheckoutView,
                        category_detail_view,
                        order_detail_view,
                        user_orders_view,
                        render_home_page)

from django.conf.urls.i18n import i18n_patterns
from users.views import register_view, login_view, logout_view
from payments.views import CheckoutSession, CustomerPortalView, WebhookView, CheckoutPaymentPage, checkout_success_page
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from Book.api_views import BookViewSet, OrderViewSet, CartViewSet, CategoryViewSet, BookReviewViewSet
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


router = DefaultRouter()
router.register("books", BookViewSet, basename="book")
router.register("categories", CategoryViewSet, basename="category")
router.register("orders", OrderViewSet, basename="order")
router.register("cart", CartViewSet, basename="cart")
router.register("reviews", BookReviewViewSet, basename="review")

def trigger_error(request):
    division_by_zero = 1 / 0
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),
    path('webhook/', WebhookView.as_view(), name='webhook'),
    path('create-checkout-session/', CheckoutSession.as_view(), name='checkout_session'),
    path('customer-portal/', CustomerPortalView.as_view(), name='customer_portal'),
    path('checkout-payment/', CheckoutPaymentPage.as_view(), name='checkout_payment'),
    path('success.html', checkout_success_page, name='checkout_success'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('sentry-debug/', trigger_error),

]



urlpatterns += i18n_patterns(
    path('', render_home_page, name='home'),

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
    path('category/<slug:slug>/', category_detail_view, name='category_detail'),
    path('order/<int:pk>/', order_detail_view, name='order_detail'),
    path('my-orders/', user_orders_view, name='user_orders'),
    prefix_default_language=True,
)
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
