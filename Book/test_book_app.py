import datetime
import pytest
from decimal import Decimal
from django.urls import reverse

from Book.models import Book, Category, Order, OrderItem
from Book.forms import BookSeachForm, CheckoutForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    return Category.objects.create(name="Фантастика", slug="fantastika")


@pytest.fixture
def book(category):
    return Book.objects.create(
        title="lgkgk", author="fwafwf",
        year_of_manufacture=datetime.date(1965, 1, 1),
        price=Decimal("350.00"), stock=10, category=category,
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="testuser", password="pass123")


@pytest.fixture
def order(user):
    return Order.objects.create(user=user, total_price=Decimal("350.00"), post_office_number="12345")



def test_category_str(category):
    assert str(category) == "Фантастика"


def test_book_str(book):
    assert str(book) == f"Book {book.id} - Дюна"


def test_book_default_stock_zero(category):
    b = Book.objects.create(title="dwdwad", author="wadwad", year_of_manufacture=datetime.date(2000, 1, 1),
                            price=Decimal("10.00"), category=category)
    assert b.stock == 0


def test_order_default_status(order):
    assert order.status == "pending"


def test_order_item_str(order, book):
    item = OrderItem.objects.create(order=order, book=book, quantity=2)
    assert str(item) == f"2 of {book.title} in order {order.id}"




def test_book_search_form_valid(category):
    form = BookSeachForm(data={"title": "awdw", "author": "fwafawf", "category": category.pk})
    assert form.is_valid()


def test_book_search_form_invalid_empty():
    assert not BookSeachForm(data={}).is_valid()


def test_checkout_form_valid():
    form = CheckoutForm(data={"payment_method": "card", "post_office_number": "12345"})
    assert form.is_valid()


def test_checkout_form_invalid_payment_method():
    form = CheckoutForm(data={"payment_method": "bitcoin", "post_office_number": "12345"})
    assert not form.is_valid()


def test_checkout_form_missing_post_office():
    form = CheckoutForm(data={"payment_method": "card", "post_office_number": ""})
    assert not form.is_valid()

def test_book_list_status_ok(client, book):
    assert client.get(reverse("book_list")).status_code == 200


def test_book_list_contains_book(client, book):
    response = client.get(reverse("book_list"))
    assert book in response.context["books"]


def test_book_list_search_filters(client, book):
    response = client.get(reverse("book_list"), {"q": "Нет такой"})
    assert book not in response.context["books"]


def test_book_detail_status_ok(client, book):
    response = client.get(reverse("book_detail", kwargs={"pk": book.pk}))
    assert response.status_code == 200


def test_cart_add_creates_entry(client, book):
    client.get(reverse("cart_add", kwargs={"pk": book.pk}))
    assert client.session["cart"] == {str(book.pk): 1}


def test_cart_add_increments(client, book):
    client.get(reverse("cart_add", kwargs={"pk": book.pk}))
    client.get(reverse("cart_add", kwargs={"pk": book.pk}))
    assert client.session["cart"] == {str(book.pk): 2}


def test_cart_remove(client, book):
    client.get(reverse("cart_add", kwargs={"pk": book.pk}))
    client.get(reverse("cart_remove", kwargs={"book_id": book.pk}))
    assert str(book.pk) not in client.session.get("cart", {})


def test_clear_cart(client, book):
    client.get(reverse("cart_add", kwargs={"pk": book.pk}))
    client.get(reverse("clear_cart"))
    assert client.session["cart"] == {}


def test_checkout_requires_login(client, book):
    response = client.get(reverse("checkout"))
    assert response.status_code == 302


def test_checkout_post_creates_order(client, user, book):
    client.force_login(user)
    session = client.session
    session["cart"] = {str(book.pk): 1}
    session.save()

    response = client.post(reverse("checkout"), {
        "payment_method": "card", "post_office_number": "54321",
    })
    assert response.status_code == 302
    assert Order.objects.filter(user=user).exists()