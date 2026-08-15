from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import requests
from .models import Book, BookReview, Order



@receiver([post_save, post_delete], sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    cache.delete(f"book_detail_{instance.pk}")


@receiver([post_save, post_delete], sender=BookReview)
def invalidate_review_cache(sender, instance, **kwargs):
    cache.delete(f"book_avg_rating_{instance.book_id}")
    cache.delete(f"book_detail_{instance.book_id}")

@receiver(post_save, sender=Order)
def notify_analytics(sender, instance, created, **kwargs):
    if created:
        try:
            requests.post("http://project-b-web:8000/api/purchases/", json={
                "user_id": instance.user_id,
                "order_id": instance.id,
                "amount": str(instance.total_price),
            }, timeout=3)
        except requests.exceptions.RequestException as e:
            print(f"Analytics service unavailable: {e}")
