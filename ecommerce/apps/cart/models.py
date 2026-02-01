from django.db import models
from django.db.models import Sum, F
from django.conf import settings
from apps.common.models import TimeStampedModel
from apps.products.models import Product
from decimal import Decimal


class Cart(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_items(self) -> int:
        """
        Get total number of items in cart using DB aggregation.
        Single query instead of Python iteration.
        """
        result = self.items.aggregate(total=Sum("quantity"))
        return result["total"] or 0

    @property
    def subtotal(self) -> Decimal:
        """
        Calculate cart subtotal using DB aggregation.
        Single query with F() expression for price * quantity.
        """
        result = self.items.aggregate(total=Sum(F("quantity") * F("product__price")))
        return Decimal(str(result["total"] or 0))

    def clear(self):
        self.items.all().delete()


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        # Validate quantity against available stock
        if hasattr(self.product, "inventory"):
            if self.quantity > self.product.inventory.available:
                raise ValueError(
                    f"Insufficient stock. Available: {self.product.inventory.available}"
                )
        super().save(*args, **kwargs)
