from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.utils import DataError
from django.test import TestCase

from Book.models import Book, Category, Order, OrderItem

User = get_user_model()


class CategoryModelTest(TestCase):
    """Тести для моделі Category."""

    def setUp(self):
        # Generated with AI, reviewed and modified
        self.category = Category.objects.create(name='Fantasy', slug='fantasy')

    def test_str_representation(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(str(self.category), 'Fantasy')

    def test_category_created_with_correct_fields(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(self.category.name, 'Fantasy')
        self.assertEqual(self.category.slug, 'fantasy')

    def test_slug_must_be_unique(self):
        # Generated with AI, reviewed and modified
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name='Fantasy 2', slug='fantasy')

    def test_category_can_be_retrieved_by_slug(self):
        # Generated with AI, reviewed and modified
        fetched = Category.objects.get(slug='fantasy')
        self.assertEqual(fetched.pk, self.category.pk)


class BookModelTest(TestCase):
    """Тести для моделі Book."""

    def setUp(self):
        # Generated with AI, reviewed and modified
        self.category = Category.objects.create(name='Sci-Fi', slug='sci-fi')
        self.book = Book.objects.create(
            title='Dune',
            author='Frank Herbert',
            year_of_manufacture=date(1965, 8, 1),
            price=Decimal('19.99'),
            description='A science fiction novel.',
            stock=5,
            category=self.category,
        )

    def test_str_representation(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(str(self.book), f'Book {self.book.id} - Dune')

    def test_book_fields_saved_correctly(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(self.book.title, 'Dune')
        self.assertEqual(self.book.author, 'Frank Herbert')
        self.assertEqual(self.book.price, Decimal('19.99'))
        self.assertEqual(self.book.stock, 5)
        self.assertEqual(self.book.category, self.category)

    def test_default_stock_is_zero(self):
        # Generated with AI, reviewed and modified
        book = Book.objects.create(
            title='No Stock Book',
            author='Some Author',
            year_of_manufacture=date(2020, 1, 1),
            price=Decimal('9.99'),
            category=self.category,
        )
        self.assertEqual(book.stock, 0)

    def test_description_can_be_blank(self):
        # Generated with AI, reviewed and modified
        book = Book.objects.create(
            title='No Description',
            author='Some Author',
            year_of_manufacture=date(2021, 1, 1),
            price=Decimal('5.00'),
            category=self.category,
        )
        self.assertIsNone(book.description)

    def test_book_deleted_when_category_deleted(self):
        # Generated with AI, reviewed and modified
        # category FK uses on_delete=CASCADE, so deleting the category
        # must remove dependent books too.
        self.category.delete()
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_book_requires_category(self):
        # Generated with AI, reviewed and modified
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Book.objects.create(
                    title='Orphan Book',
                    author='Nobody',
                    year_of_manufacture=date(2022, 1, 1),
                    price=Decimal('3.00'),
                    category=None,
                )


class OrderModelTest(TestCase):
    """Тести для моделі Order."""

    def setUp(self):
        # Generated with AI, reviewed and modified
        self.user = User.objects.create_user(username='reader', password='pass12345')
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('49.98'),
            post_office_number='101',
        )

    def test_str_representation(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(str(self.order), f'Order {self.order.id} by reader')

    def test_default_payment_method_is_card(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(self.order.payment_method, 'card')

    def test_default_payment_status_is_unpaid(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(self.order.payment_status, 'unpaid')

    def test_default_status_is_pending(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(self.order.status, 'pending')

    def test_created_at_is_set_automatically(self):
        # Generated with AI, reviewed and modified
        self.assertIsNotNone(self.order.created_at)

    def test_order_deleted_when_user_deleted(self):
        # Generated with AI, reviewed and modified
        # user FK uses on_delete=CASCADE
        self.user.delete()
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_order_status_can_be_updated(self):
        # Generated with AI, reviewed and modified
        self.order.status = 'completed'
        self.order.save()
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')


class OrderItemModelTest(TestCase):
    """Тести для моделі OrderItem."""

    def setUp(self):
        # Generated with AI, reviewed and modified
        self.user = User.objects.create_user(username='buyer', password='pass12345')
        self.category = Category.objects.create(name='Drama', slug='drama')
        self.book = Book.objects.create(
            title='Hamlet',
            author='William Shakespeare',
            year_of_manufacture=date(1603, 1, 1),
            price=Decimal('12.50'),
            stock=10,
            category=self.category,
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('25.00'),
            post_office_number='202',
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            quantity=2,
        )

    def test_str_representation(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(
            str(self.order_item),
            f'2 of Hamlet in order {self.order.id}',
        )

    def test_order_item_fields_saved_correctly(self):
        # Generated with AI, reviewed and modified
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.book, self.book)
        self.assertEqual(self.order_item.quantity, 2)

    def test_order_item_deleted_when_order_deleted(self):
        # Generated with AI, reviewed and modified
        self.order.delete()
        self.assertFalse(OrderItem.objects.filter(pk=self.order_item.pk).exists())

    def test_order_item_deleted_when_book_deleted(self):
        # Generated with AI, reviewed and modified
        self.book.delete()
        self.assertFalse(OrderItem.objects.filter(pk=self.order_item.pk).exists())

    def test_quantity_must_be_positive(self):
        # Generated with AI, reviewed and modified
        # quantity uses PositiveIntegerField; negative values are rejected
        # at the DB level (SQLite enforces the CHECK constraint Django adds).
        with self.assertRaises((IntegrityError, DataError)):
            with transaction.atomic():
                OrderItem.objects.create(
                    order=self.order,
                    book=self.book,
                    quantity=-1,
                )

    def test_order_can_have_multiple_items(self):
        # Generated with AI, reviewed and modified
        second_book = Book.objects.create(
            title='Macbeth',
            author='William Shakespeare',
            year_of_manufacture=date(1606, 1, 1),
            price=Decimal('11.00'),
            category=self.category,
        )
        OrderItem.objects.create(order=self.order, book=second_book, quantity=1)
        self.assertEqual(self.order.orderitem_set.count(), 2)