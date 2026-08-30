from cart.cart import Cart
from django.shortcuts import render
from .forms import OrderCreateForm
from .models import OrderItem

# Import the asynchronous task
from .tasks import order_created


def order_create(request):
    """
    Handle the checkout process:
    - GET request: display an empty order form.
    - POST request: validate data, persist the order, and clear the cart.
    """
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # 1. Save the customer details as a new Order record
            order = form.save()

            # 2. Persist each cart item as an OrderItem in the database
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )

            # 3. Empty the session cart after a successful order
            cart.clear()

            # 4. Send the confirmation email asynchronously:
            #    .delay() serializes the arguments, pushes the message to
            #    RabbitMQ, and returns IMMEDIATELY without waiting for the email.
            order_created.delay(order.id)

            # 5. Render the success (thank-you) page
            return render(
                request,
                'orders/order/created.html',
                {'order': order},
            )
    else:
        # Instantiate an empty form for GET requests
        form = OrderCreateForm()

    # Fallback response for GET requests or invalid form submissions
    return render(
        request,
        'orders/order/create.html',
        {'cart': cart, 'form': form},
    )