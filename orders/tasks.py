from celery import shared_task
from django.core.mail import send_mail

from .models import Order

@shared_task
def order_created(order_id):
    """
    Task to send an email notification when an order
    is successfully created.
    """
    # Fetch the order inside the worker to avoid stale data
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    message = (
        f'Dear {order.first_name},\n\n'
        f'You have successfully placed an order. '
        f'Your order ID is {order.id}.'
    )
    # Send the email; returns 1 on success
    mail_sent = send_mail(
        subject,
        message,
        'admin@myshop.com',
        [order.email]
    )
    return mail_sent