from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Book, BookReview


@receiver([post_save, post_delete], sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    cache.delete(f"book_detail_{instance.pk}")


@receiver([post_save, post_delete], sender=BookReview)
def invalidate_review_cache(sender, instance, **kwargs):
    cache.delete(f"book_avg_rating_{instance.book_id}")
    cache.delete(f"book_detail_{instance.book_id}")
