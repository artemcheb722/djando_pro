from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from Book.models import Order

@shared_task
def send_order_confirmation_email(order_id):
    order = Order.objects.select_related('user').get(pk=order_id)
    subject = f"Заказ №{order.id} оформлен"
    context = {"order": order}

    html_content = render_to_string("order_confirmation.html", context)
    text_content = f"Заказ №{order.id} оформлен. Спасибо за покупку!"

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
