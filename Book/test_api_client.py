from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from Book.models import Book, Category, Order

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category():
    return Category.objects.create(name="Fantasy", slug="fantasy")


@pytest.fixture
def book(category):
    return Book.objects.create(
        title="Test book",
        author="Test author",
        year_of_manufacture=date(2020, 1, 1),
        price=Decimal("100.00"),
        description="Test description",
        stock=5,
        category=category,
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="user", password="pass12345")


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="admin", password="pass12345", is_staff=True
    )


@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create_user(
        username="another", password="pass12345"
    )


@pytest.fixture
def book_data(category):
    return {
        "title": "New book",
        "author": "New author",
        "year_of_manufacture": "2026-06-06",
        "price": "250.00",
        "description": "New description",
        "stock": 3,
        "category": category.id,
    }


def test_categories_list_ok(api_client, category):
    assert api_client.get("/api/categories/").status_code == status.HTTP_200_OK


def test_categories_list_has_item(api_client, category):
    response = api_client.get("/api/categories/")
    assert response.data["results"][0]["slug"] == category.slug


def test_category_detail_ok(api_client, category):
    assert (
        api_client.get(f"/api/categories/{category.slug}/").status_code
        == status.HTTP_200_OK
    )


def test_category_detail_name(api_client, category):
    response = api_client.get(f"/api/categories/{category.slug}/")
    assert response.data["name"] == "Fantasy"


def test_category_create_requires_auth(api_client):
    response = api_client.post(
        "/api/categories/", {"name": "Драма", "slug": "drama"}, format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_category_create_by_staff(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    response = api_client.post(
        "/api/categories/", {"name": "Drama", "slug": "drama"}, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_category_update_by_staff(api_client, staff_user, category):
    api_client.force_authenticate(user=staff_user)
    response = api_client.patch(
        f"/api/categories/{category.slug}/", {"name": "Sci-fi"}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK


def test_category_delete_requires_auth(api_client, category):
    assert (
        api_client.delete(f"/api/categories/{category.slug}/").status_code
        == status.HTTP_401_UNAUTHORIZED
    )


def test_books_list_ok(api_client, book):
    assert api_client.get("/api/books/").status_code == status.HTTP_200_OK


def test_books_list_has_item(api_client, book):
    response = api_client.get("/api/books/")
    assert response.data["results"][0]["title"] == book.title


def test_book_detail_ok(api_client, book):
    assert api_client.get(f"/api/books/{book.id}/").status_code == status.HTTP_200_OK


def test_book_detail_author(api_client, book):
    response = api_client.get(f"/api/books/{book.id}/")
    assert response.data["author"] == book.author


def test_book_not_found(api_client):
    assert api_client.get("/api/books/99999/").status_code == status.HTTP_404_NOT_FOUND


def test_book_create_requires_auth(api_client, book_data):
    response = api_client.post("/api/books/", book_data, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_book_create_by_staff(api_client, staff_user, book_data):
    api_client.force_authenticate(user=staff_user)
    response = api_client.post("/api/books/", book_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


def test_book_update_by_staff(api_client, staff_user, book):
    api_client.force_authenticate(user=staff_user)
    response = api_client.patch(f"/api/books/{book.id}/", {"stock": 10}, format="json")
    assert response.status_code == status.HTTP_200_OK


def test_book_delete_by_staff(api_client, staff_user, book):
    api_client.force_authenticate(user=staff_user)
    response = api_client.delete(f"/api/books/{book.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_cart_empty_ok(api_client):
    assert api_client.get("/api/cart/").status_code == status.HTTP_200_OK


def test_cart_empty_has_no_items(api_client):
    response = api_client.get("/api/cart/")
    assert response.data["items"] == []


def test_cart_add_item_ok(api_client, book):
    response = api_client.post(
        "/api/cart/add_item/", {"book_id": book.id}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK


def test_cart_add_item_sets_quantity(api_client, book):
    response = api_client.post(
        "/api/cart/add_item/", {"book_id": book.id, "quantity": 2}, format="json"
    )
    assert response.data["cart"][str(book.id)] == 2


def test_cart_add_item_twice_sums_quantity(api_client, book):
    api_client.post("/api/cart/add_item/", {"book_id": book.id}, format="json")
    response = api_client.post(
        "/api/cart/add_item/", {"book_id": book.id}, format="json"
    )
    assert response.data["cart"][str(book.id)] == 2


def test_cart_list_shows_item(api_client, book):
    api_client.post("/api/cart/add_item/", {"book_id": book.id}, format="json")
    response = api_client.get("/api/cart/")
    assert response.data["items"][0]["book"]["id"] == book.id


def test_cart_remove_item(api_client, book):
    api_client.post("/api/cart/add_item/", {"book_id": book.id}, format="json")
    response = api_client.post(
        "/api/cart/remove_item/", {"book_id": book.id}, format="json"
    )
    assert str(book.id) not in response.data["cart"]


def test_cart_remove_missing_item_ok(api_client):
    response = api_client.post(
        "/api/cart/remove_item/", {"book_id": 99999}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK


def test_cart_clear_ok(api_client, book):
    api_client.post("/api/cart/add_item/", {"book_id": book.id}, format="json")
    assert (
        api_client.post("/api/cart/clear/", format="json").status_code
        == status.HTTP_200_OK
    )


def test_cart_clear_removes_items(api_client, book):
    api_client.post("/api/cart/add_item/", {"book_id": book.id}, format="json")
    api_client.post("/api/cart/clear/", format="json")
    assert api_client.get("/api/cart/").data["items"] == []


def test_orders_list_requires_auth(api_client):
    assert api_client.get("/api/orders/").status_code == status.HTTP_401_UNAUTHORIZED


def test_orders_list_ok_for_user(api_client, user):
    api_client.force_authenticate(user=user)
    assert api_client.get("/api/orders/").status_code == status.HTTP_200_OK


def test_orders_show_only_own(api_client, user, another_user):
    own_order = Order.objects.create(
        user=user, total_price="100.00", post_office_number="1"
    )
    Order.objects.create(
        user=another_user, total_price="200.00", post_office_number="2"
    )
    api_client.force_authenticate(user=user)
    response = api_client.get("/api/orders/")
    assert response.data["results"][0]["id"] == own_order.id


def test_orders_staff_sees_all(api_client, staff_user, user, another_user):
    Order.objects.create(user=user, total_price="100.00", post_office_number="1")
    Order.objects.create(
        user=another_user, total_price="200.00", post_office_number="2"
    )
    api_client.force_authenticate(user=staff_user)
    assert len(api_client.get("/api/orders/").data["results"]) == 2


def test_login_returns_tokens(api_client, user):
    response = api_client.post(
        "/api/auth/login/",
        {"username": user.username, "password": "pass12345"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
