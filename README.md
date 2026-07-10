# djando_pro

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

