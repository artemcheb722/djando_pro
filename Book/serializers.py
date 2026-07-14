from rest_framework import serializers

from .models import Book, Category, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "year_of_manufacture",
            "price",
            "description",
            "stock",
            "category",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "book", "book_title", "quantity")


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    items = OrderItemSerializer(source="orderitem_set", many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "total_price",
            "created_at",
            "post_office_number",
            "payment_method",
            "payment_status",
            "status",
            "items",
        )
        read_only_fields = ("created_at")