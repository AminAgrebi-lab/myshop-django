from cart.cart import Cart
from django.shortcuts import redirect, render
from .forms import OrderCreateForm
from .models import OrderItem
# Import the asynchronous task
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
            # 1. Save the customer details as a new Order record
            order = form.save()

            # 2. Persist each cart item as an OrderItem
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )

            # 3. Empty the session cart
            cart.clear()

            # 4. Queue the async confirmation email
            order_created.delay(order.id)

            # 5. Remember the order in the session for the payment app
            request.session['order_id'] = order.id

            # 6. Redirect to the Stripe payment process
            return redirect('payment:process')
    else:
        form = OrderCreateForm()
    return render(
        request,
        'orders/order/create.html',
        {'cart': cart, 'form': form},
    )
