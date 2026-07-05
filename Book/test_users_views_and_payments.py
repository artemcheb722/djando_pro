import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="testuser", password="pass123")




def test_register_page_loads(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200


def test_register_creates_user_and_logs_in(client):
    response = client.post(reverse("register"), {
        "username": "newuser",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    })
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated is True


def test_register_invalid_data_shows_error(client):
    response = client.post(reverse("register"), {
        "username": "",
        "password1": "123",
        "password2": "456",
    })
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
    response = client.post(reverse("login"), {
        "username": "testuser", "password": "pass123",
    })
    assert response.status_code == 302


def test_login_invalid_credentials_shows_error(client, user):
    response = client.post(reverse("login"), {
        "username": "testuser", "password": "wrongpass",
    })
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