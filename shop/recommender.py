import redis
from django.conf import settings

from .models import Product

# Connect to the dedicated Redis database for recommendations
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


class Recommender:
    """
    A purchase-history-based recommendation engine backed by
    Redis sorted sets. Each product keeps a sorted set of
    other products frequently bought with it, scored by the
    number of co-purchases.
    """

    def get_product_key(self, id):
        """Return the Redis key for a product's co-purchase set."""
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        """
        Record that the given products were purchased together
        in a single order. For every pair (A, B), increment
        B's score inside A's sorted set by 1 (and vice versa).
        """
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    r.zincrby(
                        self.get_product_key(product_id), 1, with_id
                    )

    def suggest_products_for(self, products, max_results=6):
        """
        Return up to max_results products frequently bought
        together with the given products. If more than one
        product is passed, aggregate their sorted sets first.
        """
        product_ids = [p.id for p in products]

        if len(products) == 1:
            # Single product: just read its sorted set
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
                0, -1, desc=True
            )[:max_results]
        else:
            # Multiple products: aggregate then read
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            keys = [self.get_product_key(id) for id in product_ids]
            # Union + sum scores into a temporary key
            r.zunionstore(tmp_key, keys)
            # Remove products already in the cart from suggestions
            r.zrem(tmp_key, *product_ids)
            suggestions = r.zrange(
                tmp_key, 0, -1, desc=True
            )[:max_results]
            # Clean up the temporary key
            r.delete(tmp_key)

        # Look up the actual Product objects and preserve score order
        suggested_ids = [int(id) for id in suggestions]
        suggested_products = list(
            Product.objects.filter(id__in=suggested_ids)
        )
        suggested_products.sort(
            key=lambda x: suggested_ids.index(x.id)
        )
        return suggested_products

    def clear_purchases(self):
        """Wipe all recommendation data (useful for development)."""
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))