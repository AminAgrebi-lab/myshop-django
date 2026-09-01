from io import BytesIO

import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from orders.models import Order

import os
import sys

# Force Python to find GTK3 libraries before QEMU's incomplete copies
if sys.platform == 'win32':
    gtk_path = r'D:\Program Files\GTK3-Runtime Win64\bin'
    if os.path.exists(gtk_path):
        os.environ['PATH'] = gtk_path + os.pathsep + os.environ.get('PATH', '')

from io import BytesIO
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order


@shared_task
def payment_completed(order_id):
    """
    Send an e-mail with the PDF invoice attached
    when an order is successfully paid.
    """
    order = Order.objects.get(id=order_id)
    subject = f'My Shop - Invoice no. {order.id}'
    message = (
        'Please, find attached the invoice for your recent purchase.'
    )
    email = EmailMessage(
        subject, message, 'admin@myshop.com', [order.email]
    )
    # Render the invoice HTML and convert it to PDF in memory
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(finders.find('css/pdf.css'))]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # Attach the in-memory PDF and send
    email.attach(
        f'order_{order.id}.pdf', out.getvalue(), 'application/pdf'
    )
    email.send()