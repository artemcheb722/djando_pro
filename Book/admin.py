from django.contrib import admin

from .models import Book, Category

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year_of_manufacture', 'price', 'stock']
    list_filter = ['author', 'category']
    search_fields = ['title', 'author']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']


