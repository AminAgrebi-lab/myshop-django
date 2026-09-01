from django.urls import path

from payment import webhooks
from . import views

app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
        # New: Webhook endpoint for Stripe notifications
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
]
