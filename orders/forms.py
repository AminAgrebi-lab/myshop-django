from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    ModelForm to collect customer details for creating a new Order.
    """
    class Meta:
        model = Order
        # Exclude system-managed fields (created, updated, paid)
        fields = [
            'first_name', 'last_name', 'email',
            'address', 'postal_code', 'city'
        ]
