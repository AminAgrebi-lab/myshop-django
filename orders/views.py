from cart.cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

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