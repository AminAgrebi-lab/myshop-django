import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
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
        return mark_safe(html)
    return ''
order_payment.short_description = 'Stripe payment'


def export_to_csv(modeladmin, request, queryset):
    """
    Generic admin action: export the selected objects to a CSV file.
    Works with any ModelAdmin because fields are read dynamically.
    """
    opts = modeladmin.model._meta
    content_disposition = (
        f'attachment; filename={opts.verbose_name}.csv'
    )
    # Tell the browser to download the response as a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)

    # Keep only concrete fields (skip m2m and reverse relations)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]

    # Header row with human-readable field names
    writer.writerow([field.verbose_name for field in fields])

    # One row per selected object
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                # CSV needs plain strings, so format datetimes
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Register the custom CSV export action
    actions = [export_to_csv]
    list_display = [
        'id', 'first_name', 'last_name', 'email',
        'address', 'postal_code', 'city', 'paid',
        order_payment, 'created', 'updated',
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]