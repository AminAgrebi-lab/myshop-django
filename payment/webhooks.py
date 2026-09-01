import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order

@csrf_exempt
def stripe_webhook(request):
    """
    Receive Stripe events and mark orders as paid when a
    checkout session completes successfully.
    """
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        # Verify the signature: ensures the event is genuinely from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature (possible spoofing attempt)
        return HttpResponse(status=400)

    # Stage 2: react to the payment-completed event
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if (
            session.mode == 'payment'
            and session.payment_status == 'paid'
        ):
            try:
                # client_reference_id is the order id we passed at checkout
                order = Order.objects.get(
                    id=session.client_reference_id
                )
            except Order.DoesNotExist:
                return HttpResponse(status=404)

            # Mark the order as paid and persist the change
            order.paid = True
            order.save()

    return HttpResponse(status=200)