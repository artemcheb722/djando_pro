from django.contrib import admin

from .models import Book, Category, Order, OrderItem

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year_of_manufacture', 'price', 'stock']
    list_filter = ['author', 'category']
    search_fields = ['title', 'author']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'created_at', 'payment_status', 'status']
    list_filter = ['payment_status', 'status', 'created_at']
    search_fields = ['id', 'user__username', 'post_office_number']
    inlines = [OrderItemInline]
