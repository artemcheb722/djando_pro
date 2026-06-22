from django.db import models
from users.models import User

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

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    post_office_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=[('card', 'Card'), ('cash', 'Cash')], default='card')
    payment_status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending')

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity} of {self.book.title} in order {self.order.id}'