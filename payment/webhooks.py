import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order

from .tasks import payment_completed

from shop.models import Product
from shop.recommender import Recommender


@csrf_exempt
def stripe_webhook(request):
    """Receive and verify Stripe payment notifications."""
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if (
            session.mode == 'payment'
            and session.payment_status == 'paid'
        ):
            try:
                order = Order.objects.get(
                    id=session.client_reference_id
                )
            except Order.DoesNotExist:
                return HttpResponse(status=404)

            order.paid = True
            order.stripe_id = session.payment_intent
            order.save()
            order.paid = True
            order.stripe_id = session.payment_intent
            order.save()

            # Train the recommendation engine on this purchase
            product_ids = order.items.values_list('product_id')
            products = Product.objects.filter(id__in=product_ids)
            recommender = Recommender()
            recommender.products_bought(products)

            # Queue the async invoice email via Celery
            payment_completed.delay(order.id)
            # Queue the async invoice email via Celery
            payment_completed.delay(order.id)

    return HttpResponse(status=200)