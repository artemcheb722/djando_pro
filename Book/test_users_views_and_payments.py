from unittest import mock

import pytest
from django.urls import reverse

from Book.factories import OrderFactory
from payments.emails import send_order_confirmation_email

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="testuser", password="pass123"
    )


def test_register_page_loads(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200


def test_register_creates_user_and_logs_in(client):
    response = client.post(
        reverse("register"),
        {
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        },
    )
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated is True


def test_register_invalid_data_shows_error(client):
    response = client.post(
        reverse("register"),
        {
            "username": "",
            "password1": "123",
            "password2": "456",
        },
    )
    assert response.status_code == 200
    assert "error" in response.context


def test_register_redirects_if_already_logged_in(client, user):
    client.force_login(user)
    response = client.get(reverse("register"))
    assert response.status_code == 302


def test_login_page_loads(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200


def test_login_valid_credentials_redirects(client, user):
    response = client.post(
        reverse("login"),
        {
            "username": "testuser",
            "password": "pass123",
        },
    )
    assert response.status_code == 302


def test_login_invalid_credentials_shows_error(client, user):
    response = client.post(
        reverse("login"),
        {
            "username": "testuser",
            "password": "wrongpass",
        },
    )
    assert response.status_code == 200
    assert "error" in response.context


def test_logout_redirects(client, user):
    client.force_login(user)
    response = client.get(reverse("logout"))
    assert response.status_code == 302


def test_logout_actually_logs_out(client, user):
    client.force_login(user)
    client.get(reverse("logout"))
    response = client.get(reverse("checkout"))
    assert response.status_code == 302


def test_checkout_payment_page_loads(client):
    response = client.get(reverse("checkout_payment"))
    assert response.status_code == 200


def test_checkout_success_page_shows_session_id(client):
    response = client.get(reverse("checkout_success"), {"session_id": "sess_123"})
    assert response.status_code == 200
    assert response.context["session_id"] == "sess_123"


def test_checkout_session_without_lookup_key(client):
    response = client.post(reverse("checkout_session"), {})
    assert response.status_code == 400
    assert response.json()["error"] == "Missing lookup_key"


@pytest.mark.django_db
@mock.patch("payments.emails.EmailMultiAlternatives.send")
def test_order_sends_email(mock_send):
    order = OrderFactory()
    send_order_confirmation_email(order)
    assert mock_send.called


@pytest.mark.django_db
@mock.patch("payments.views.client")
def test_checkout_redirects(mock_client, client):
    mock_client.v1.prices.list.return_value.data = [mock.Mock(id="price_123")]
    mock_client.v1.checkout.sessions.create.return_value.url = (
        "https://checkout.stripe.com/pay/cs_test_123"
    )

    response = client.post(reverse("checkout_session"), {"lookup_key": "pro_monthly"})

    assert response.status_code == 302
    assert response.url == "https://checkout.stripe.com/pay/cs_test_123"


@pytest.mark.django_db
@mock.patch("payments.views.client")
def test_webhook_ok(mock_client, client):
    mock_client.construct_event.return_value = {
        "type": "checkout.session.completed",
        "data": {"object": {}},
    }

    response = client.post(
        reverse("webhook"),
        data="{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="sig",
    )

    assert response.status_code == 200
