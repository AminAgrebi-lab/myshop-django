import os
import sys

# Force Python to find GTK3 libraries before QEMU's incomplete copies
if sys.platform == 'win32':
    gtk_path = r'D:\Program Files\GTK3-Runtime Win64\bin'
    if os.path.exists(gtk_path):
        os.environ['PATH'] = gtk_path + os.pathsep + os.environ.get('PATH', '')

# Now import everything else
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint  # This will now find the correct GTK3 libraries

from cart.cart import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


def order_create(request):
    """
    Handle checkout: persist the order, queue the confirmation
    email, then redirect the customer to the payment process.
    """
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()
            # Queue the async confirmation email
            order_created.delay(order.id)
            # Remember the order in the session for the payment app
            request.session['order_id'] = order.id
            return redirect('payment:process')
    else:
        form = OrderCreateForm()
    return render(
        request,
        'orders/order/create.html',
        {'cart': cart, 'form': form},
    )


@staff_member_required
def admin_order_detail(request, order_id):
    """
    Custom admin view displaying the full details of an order.
    Only accessible to active staff users.
    """
    order = get_object_or_404(Order, id=order_id)
    return render(
        request,
        'admin/orders/order/detail.html',
        {'order': order},
    )


@staff_member_required
def admin_order_pdf(request, order_id):
    """Generate and download a PDF invoice for the given order."""
    order = get_object_or_404(Order, id=order_id)
    # Render the HTML invoice with the order data
    html = render_to_string('orders/order/pdf.html', {'order': order})
    # Response the browser treats as a downloadable PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    # HTML -> PDF, streamed straight into the response
    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=[weasyprint.CSS(finders.find('css/pdf.css'))],
    )
    return response
