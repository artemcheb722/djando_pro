# Django Pro Bookstore & Analytics

[![CI](https://github.com/artemcheb722/django_pro/actions/workflows/ci.yml/badge.svg)](https://github.com/artemcheb722/django_pro/actions/workflows/ci.yml)
[![Tests](https://github.com/artemcheb722/django_pro/actions/workflows/tests.yml/badge.svg)](https://github.com/artemcheb722/django_pro/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/artemcheb722/django_pro/branch/main/graph/badge.svg)](https://codecov.io/gh/artemcheb722/django_pro)

This repository contains a containerized Django bookstore and a separate **Project B** analytics service. The bookstore provides the customer-facing catalog, cart, orders, authentication, and Stripe payment flow. When an order is created, it notifies Project B through a Django REST Framework API. Project B records purchase events and exposes per-user purchase statistics in JSON and in a web dashboard.

## Architecture

```text
Browser / API client
        |
        v
Bookstore (Django, :8000) ─── PostgreSQL / Redis / Celery
        |
        | POST /api/purchases/
        v
Project B Analytics (Django REST Framework, :8001)
        |
        v
Analytics PostgreSQL database
```

All services are connected to the same Docker bridge network. Inside that network the bookstore reaches analytics at `http://project-b-web:8000/api/purchases/`; from the host machine, Project B is available at `http://localhost:8001`.

## Features

### Bookstore

- Browse books and categories, including localized English and Russian routes.
- Register, sign in, and sign out with the custom user model.
- Use a session-based shopping cart and create orders.
- View order history and order details.
- Manage books, categories, orders, and users through Django Admin.
- Access a REST API for books, categories, cart, orders, and reviews.
- Authenticate API requests using JWT access and refresh tokens.
- Use Stripe Checkout, customer portal, and webhook endpoints.
- Serve OpenAPI schema, Swagger UI, and ReDoc documentation.
- Cache book-related data in Redis and invalidate relevant cache keys after book or review changes.
- Run a scheduled Celery task that clears expired Django sessions daily.

### Project B analytics

- Accept purchase events from the bookstore through a REST endpoint.
- Persist `user_id`, `order_id`, amount, and creation date for every received event.
- Aggregate total amount spent and number of orders per user.
- Provide the aggregated data as JSON and render it in a dashboard.

## Services and ports

| Service | Purpose | Host port |
| --- | --- | --- |
| `nginx` | Reverse proxy and static/media delivery | `80` |
| `web` | Main bookstore Django application | `8000` |
| `project-b-web` | Project B analytics Django application | `8001` |
| `database` | Main PostgreSQL database | `6655` |
| `redis` | Cache, Celery broker, and result backend | `6379` |
| `celery` | Background-task worker | — |
| `celery-beat` | Scheduled-task scheduler | — |

## Technology stack

- Python 3.12 and Django
- Django REST Framework, Simple JWT, django-filter, and drf-spectacular
- PostgreSQL and Redis
- Celery and Celery Beat
- Stripe
- Docker Compose, Gunicorn, Nginx, and WhiteNoise
- pytest, pytest-django, pytest-cov, and factory-boy

## Prerequisites

- Docker Engine with Docker Compose v2
- GNU Make (optional, for the provided shortcuts)
- Stripe credentials if payment endpoints will be used

## Configuration

1. Create the main service environment file:

   ```bash
   cp .env_example .env
   ```

2. Fill in the required values in `.env`. At a minimum, configure the PostgreSQL variables, `REDIS_PASSWORD`, `DJANGO_SECRET_KEY`, and `STRIPE_SECRET_KEY` when using Stripe.

3. Create `project_b/.env` for the analytics service. It needs the database variables used by `project_b/config/settings.py`:

   ```dotenv
   POSTGRES_HOST=database
   POSTGRES_PORT=5432
   POSTGRES_DATABASE=analytics_db
   POSTGRES_USER=analytics_user
   POSTGRES_PASSWORD=change-me
   ```

   The analytics service is configured as a standalone Django project and may use its own PostgreSQL database. Ensure the referenced database is reachable from the `project-b-web` container.

> Never commit real `.env` files, Stripe keys, passwords, or production secrets.

## Run with Docker Compose

Build and start the complete system:

```bash
make build
make up
```

In a second terminal, apply migrations for the bookstore:

```bash
make migrate
```

The containers run migrations on startup as well. Main entry points:

- Storefront: `http://localhost:8000/`
- Django Admin: `http://localhost:8000/admin/`
- Main API documentation: `http://localhost:8000/api/docs/`
- Analytics dashboard: `http://localhost:8001/api/dashboard/`
- Analytics JSON API: `http://localhost:8001/api/user-stats/`

Useful commands:

```bash
make createsuperuser
make test
make down
```

To run without Make, use the equivalent `docker compose` commands, for example `docker compose up --build`.

## How the analytics integration works

1. A customer creates an `Order` in the bookstore.
2. The `post_save` signal in `Book/signals.py` detects a newly created order.
3. It sends a JSON request to Project B:

   ```json
   {
     "user_id": 42,
     "order_id": 105,
     "amount": "39.99"
   }
   ```

4. `POST /api/purchases/` in Project B stores the event as a `UserPurchase` record.
5. `GET /api/user-stats/` groups records by `user_id` and returns `total_spent` and `orders_count`.

The notification uses a three-second timeout. If Project B is unavailable, the bookstore logs the error and continues processing the order.

## API reference

### Main bookstore API (`http://localhost:8000`)

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET`, `POST` | `/api/books/` | List books or create a book (admin only for writes) |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/books/{id}/` | Retrieve or manage a book |
| `GET`, `POST` | `/api/categories/` | List categories or create a category |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/categories/{slug}/` | Retrieve or manage a category |
| `GET` | `/api/cart/` | Get the current session cart |
| `POST` | `/api/cart/add_item/` | Add a book to the session cart |
| `POST` | `/api/cart/remove_item/` | Remove a book from the session cart |
| `POST` | `/api/cart/clear/` | Clear the session cart |
| `GET`, `POST` | `/api/orders/` | List the current user's orders or create one |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/orders/{id}/` | Retrieve or manage an order according to permissions |
| `POST` | `/api/auth/login/` | Obtain JWT access and refresh tokens |
| `POST` | `/api/auth/refresh/` | Refresh a JWT access token |
| `GET` | `/api/schema/` | OpenAPI schema |
| `GET` | `/api/docs/` | Swagger UI |
| `GET` | `/api/redoc/` | ReDoc |

Use `Authorization: Bearer <access_token>` for endpoints that require authentication. The generated documentation at `/api/docs/` is the source of truth for request and response schemas.

Example: obtain a token:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your-user","password":"your-password"}'
```

Example: add an item to the session cart:

```bash
curl -X POST http://localhost:8000/api/cart/add_item/ \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "quantity": 2}'
```

### Project B analytics API (`http://localhost:8001`)

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/purchases/` | Record a purchase event |
| `GET` | `/api/user-stats/` | Return aggregated spend and order count per user |
| `GET` | `/api/dashboard/` | Render the HTML analytics dashboard |

Example response from `GET /api/user-stats/`:

```json
[
  {
    "user_id": 42,
    "total_spent": 119.97,
    "orders_count": 3
  }
]
```

## Testing and code quality

Run the test suite in the web container:

```bash
make test
```

The pytest configuration collects coverage for `Book`, `users`, and `payments` and writes `coverage.xml`. Formatting and linting shortcuts are also available:

```bash
make check
```

## Project layout

```text
Book/                   Book catalog, cart, orders, REST API, signals, and tasks
users/                  Custom user model and authentication views
payments/               Stripe Checkout, portal, and webhook views
mysite/                 Main Django project settings, routes, and Celery setup
project_b/              Independent analytics Django project
project_b/apps/analytics/  Purchase-event API and dashboard
nginx/                  Nginx reverse-proxy configuration
locale/                 English and Russian translations
docker-compose.yml      Complete multi-service local environment
```

## Operational notes

- Create a Django superuser before accessing the admin panel.
- The development environment enables Django Debug Toolbar and uses local-memory caching; the containerized base setup uses Redis.
- Configure Stripe webhook signing secrets and public application URLs appropriately before production deployment.
- Configure production `ALLOWED_HOSTS`, CORS origins, email settings, database TLS/access, and secret management before exposing the application publicly.
