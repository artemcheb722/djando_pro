from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Category, Order, BookReview
from .serializers import BookSerializer, CategorySerializer, OrderSerializer, BookReviewSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"



class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        cart = request.session.get("cart", {})
        books = Book.objects.filter(id__in=cart.keys())

        items = []
        total_price = 0
        for book in books:
            quantity = cart[str(book.id)]
            items.append({
                "book": BookSerializer(book).data,
                "quantity": quantity,
                "item_total_price": book.price * quantity,
            })
            total_price += book.price * quantity

        return Response({"items": items, "total_price": total_price})

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        book_id = str(request.data.get("book_id"))
        quantity = int(request.data.get("quantity", 1))

        cart = request.session.get("cart", {})
        cart[book_id] = cart.get(book_id, 0) + quantity
        request.session["cart"] = cart

        return Response({"detail": "Товар добавлено в корзину.", "cart": cart})

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        book_id = str(request.data.get("book_id"))
        cart = request.session.get("cart", {})
        cart.pop(book_id, None)
        request.session["cart"] = cart

        return Response({"detail": "Товар удалено из корзины.", "cart": cart})

    @action(detail=False, methods=["post"])
    def clear(self, request):
        request.session["cart"] = {}
        return Response({"detail": "Корзину очищено."})

class BookReviewViewSet(viewsets.ModelViewSet):
    serializer_class = BookReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        book_id = self.kwargs.get("book_id")
        return BookReview.objects.filter(book_id=book_id)

    def perform_create(self, serializer):
        book_id = self.kwargs.get("book_id")
        serializer.save(user=self.request.user, book_id=book_id)