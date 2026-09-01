from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Inline class to display and edit OrderItems directly on the Order page.
    """
    model = OrderItem
    raw_id_fields = ['product']


def order_payment(obj):
    """Display a clickable link to the Stripe payment dashboard."""
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        # mark_safe: render this trusted HTML as-is (no auto-escaping)
        return mark_safe(html)
    return ''
order_payment.short_description = 'Stripe payment'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'email',
        'address', 'postal_code', 'city', 'paid',
        order_payment, 'created', 'updated',   # <-- clickable column added
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
