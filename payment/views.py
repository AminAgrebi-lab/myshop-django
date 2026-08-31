from decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from orders.models import Order

# Authenticate all Stripe API calls with the secret key
stripe.api_key = settings.STRIPE_SECRET_KEY
# Pin the Stripe API version for consistent behavior
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    """
    GET: display the order summary with a 'Pay now' button.
    POST: create a Stripe Checkout Session and redirect to Stripe.
    """
    # Retrieve the order id stored in the session by order_create
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Absolute URLs for Stripe to redirect back to our shop
        success_url = request.build_absolute_uri(
            reverse('payment:completed')
        )
        cancel_url = request.build_absolute_uri(
            reverse('payment:canceled')
        )

        # Data describing the checkout session
        session_data = {
            'mode': 'payment',                # one-time payment
            'client_reference_id': order.id,  # links Stripe payment to our order
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],                 # populated below
        }

        # Add every order item to the session line items
        for item in order.items.all():
            session_data['line_items'].append(
                {
                    'price_data': {
                        # Stripe expects amounts in cents (smallest unit)
                        'unit_amount': int(item.price * Decimal('100')),
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        },
                    },
                    'quantity': item.quantity,
                }
            )

        # Create the session on Stripe's servers
        session = stripe.checkout.Session.create(**session_data)

        # 303 See Other: browser must follow the redirect with a GET
        return redirect(session.url, code=303)
    else:
        # GET: show the order summary page
        return render(request, 'payment/process.html', locals())

def payment_completed(request):
    """Landing page after a successful payment."""
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    """Landing page when the payment is canceled."""
    return render(request, 'payment/canceled.html')
