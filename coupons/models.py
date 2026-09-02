from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Coupon(models.Model):
    """
    A redeemable discount code with a validity time frame.
    """
    # The code customers type at checkout; must be unique
    code = models.CharField(max_length=50, unique=True)
    # When the coupon starts being valid
    valid_from = models.DateTimeField()
    # When the coupon expires
    valid_to = models.DateTimeField()
    # Percentage discount (0-100), guarded by validators
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage value (0 to 100)'
    )
    # Kill-switch: deactivate a coupon without deleting it
    active = models.BooleanField()

    def __str__(self):
        return self.code
