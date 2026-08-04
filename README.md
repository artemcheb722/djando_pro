# djando_pro



![CI](https://github.com/artemcheb/book-store/actions/workflows/ci.yml/badge.svg)
![Tests](https://github.com/artemcheb/book-store/actions/workflows/tests.yml/badge.svg)
![Docker](https://github.com/artemcheb/book-store/actions/workflows/docker-publish.yml/badge.svg)
![Coverage](https://codecov.io/gh/artemcheb/book-store/branch/main/graph/badge.svg)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![Docker](https://img.shields.io/badge/Docker-enabled-2496ED)

Django bookstore app: catalog, cart, checkout, payments via Stripe, registration/login.



## Structure

```
Book/       — book catalog, cart, orders (models.py, views.py)
payments/   — Stripe checkout, billing portal, webhook
users/      — registration, login, logout
mysite/     — Django project settings
locale/     — translations (en, ru)
```

## Tech stack

- Django 5.1
- PostgreSQL, Redis
- Stripe API
- Docker / docker-compose
- pytest, pytest-django, pytest-cov, factory-boy

## Running (Docker)

```bash
cp .env_example .env   # fill in POSTGRES_*, REDIS_PASSWORD, STRIPE_SECRET_KEY
make build
make up
make migrate
```

The app will be available at `http://localhost:8000`.

## Tests

```bash
make test
```

Or without Docker:

```bash
pytest -v
```

`pytest.ini` is already configured for coverage on `Book`, `users`, `payments`.

---

