import os

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"