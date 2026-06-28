from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f'Заказ №{order.id} оформлен'
    context = {'order': order}

    html_content = render_to_string('order_confirmation.html', context)
    text_content = f'Заказ №{order.id} оформлен. Спасибо за покупку!'

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()