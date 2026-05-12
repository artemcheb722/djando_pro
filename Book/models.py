from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Book title")
    author = models.CharField(max_length=200, verbose_name="Аuthor of the book")
    year_of_manufacture = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Book price")
    description = models.TextField(null=True, blank=True, verbose_name="Book description")
    stock = models.IntegerField(default=0, verbose_name="Stock")
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return f'Book {self.id} - {self.title}'


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Category name")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name