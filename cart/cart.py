from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart:
    def __init__(self, request):
        """
        Initialize the shopping cart using the current request's session.
        """
        self.session = request.session
        # Attempt to retrieve the cart from the session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # If no cart exists, create an empty dictionary in the session
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)

        # Initialize the product in the cart if it doesn't exist yet
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0, 'price': str(product.price)}

        # Update quantity based on the override flag
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        """
        Mark the session as modified to force Django to save the updated cart.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Remove a specific product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and fetch the related Product 
        instances from the database to attach them to the cart items.
        """
        product_ids = self.cart.keys()

        # Fetch all products in the cart in a single, efficient database query
        products = Product.objects.filter(id__in=product_ids)

        # Create a copy of the cart to avoid modifying the session directly
        cart = self.cart.copy()

        # Attach the Product instance to each cart item
        for product in products:
            cart[str(product.id)]['product'] = product

        # Calculate prices and yield each item
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']

            # CRITICAL: 'yield' must be indented inside this loop to make
            # the class a proper generator. Otherwise, it returns NoneType.
            yield item

    def __len__(self):
        """
        Return the total number of items in the cart (sum of quantities).
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate and return the total cost of all items in the cart.
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """
        Completely remove the cart from the user's session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
