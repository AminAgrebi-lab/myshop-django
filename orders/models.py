from django.conf import settings
from django.db import models


class Order(models.Model):
    """
    Model to store customer information and order status.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # Flag to differentiate between paid and unpaid orders later
    paid = models.BooleanField(default=False)
    # New field to store the Stripe Payment Intent ID
    stripe_id = models.CharField(max_length=250, blank=True)

    class Meta:
        # Sort orders by creation date, newest first
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        """
        Calculate the total cost by summing the cost of all related items.
        """
        return sum(item.get_cost() for item in self.items.all())

    def get_stripe_url(self):
        """
        Return the Stripe dashboard URL for the related payment.
        Handles both test and live environment URLs dynamically.
        """
        if not self.stripe_id:
            return ''
        # Check if we are in test mode by inspecting the secret key prefix
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    """
    Model to store each product bought within an order.
    """
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    # Use the string 'shop.Product' to avoid circular imports
    product = models.ForeignKey(
        'shop.Product',
        related_name='order_items',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        """
        Return the total cost for this line item (price * quantity).
        """
        return self.price * self.quantity