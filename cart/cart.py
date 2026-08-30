from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        # Store the current session to make it accessible in other methods
        self.session = request.session

        # Get the current cart from the session using the custom session ID
        cart = self.session.get(settings.CART_SESSION_ID)

        # If no cart is present in the session, create an empty cart dictionary
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        # Convert product ID to string because JSON only allows string keys
        product_id = str(product.id)

        # If the product is not in the cart, initialize it with 0 quantity and its current price
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0, 'price': str(product.price)}

        # Update the quantity based on the override_quantity flag
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        # Save the cart to the session
        self.save()

    def save(self):
        """
        Mark the session as modified to tell Django it needs to be saved.
        """
        # This tells Django that the session data has changed and must be updated in the database
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            # Delete the product key from the cart dictionary
            del self.cart[product_id]
            # Save the updated cart
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        # Get all product IDs from the cart keys
        product_ids = self.cart.keys()

        # Fetch the actual Product instances from the database in a single query
        products = Product.objects.filter(id__in=product_ids)

        # Copy the current cart dictionary to avoid modifying the session directly during iteration
        cart = self.cart.copy()

        # Attach the
