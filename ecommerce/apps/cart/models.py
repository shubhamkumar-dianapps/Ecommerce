from django.db import models
from django.db.models import Sum, F, Q
from django.conf import settings
from apps.common.models import TimeStampedModel
from apps.products.models import Product
from apps.products.constants import STATUS_PUBLISHED
from decimal import Decimal


class Cart(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )

    def __str__(self):
        return f"Cart for {self.user.email}"

    def get_valid_items(self):
        """
        Get only cart items with available products.
        Filters out deleted or unpublished products.
        """
        return self.items.filter(
            product__is_deleted=False,
            product__status=STATUS_PUBLISHED,
        )

    def get_unavailable_items(self):
        """
        Get cart items with unavailable products.
        Useful for showing warnings to user.
        """
        return self.items.filter(
            Q(product__is_deleted=True) | ~Q(product__status=STATUS_PUBLISHED)
        )

    @property
    def total_items(self) -> int:
        """
        Get total number of valid items in cart.
        Excludes deleted/unpublished products.
        """
        result = self.get_valid_items().aggregate(total=Sum("quantity"))
        return result["total"] or 0

    @property
    def subtotal(self) -> Decimal:
        """
        Calculate cart subtotal for valid items only.
        Excludes deleted/unpublished products.
        """
        result = self.get_valid_items().aggregate(
            total=Sum(F("quantity") * F("product__price"))
        )
        return Decimal(str(result["total"] or 0))

    @property
    def has_unavailable_items(self) -> bool:
        """Check if cart has any unavailable products."""
        return self.get_unavailable_items().exists()

    def remove_unavailable_items(self) -> int:
        """
        Remove cart items with deleted/unpublished products.
        Returns the number of items removed.
        """
        return self.get_unavailable_items().delete()[0]

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
        """Calculate total price, handling deleted products."""
        if self.product.is_deleted:
            return Decimal("0")
        return self.product.price * self.quantity

    @property
    def is_available(self) -> bool:
        """Check if the cart item's product is still available."""
        return (
            not self.product.is_deleted
            and self.product.status == STATUS_PUBLISHED
            and (
                not hasattr(self.product, "inventory")
                or self.product.inventory.is_in_stock
            )
        )

    def save(self, *args, **kwargs):
        # Validate quantity against available stock
        if hasattr(self.product, "inventory"):
            if self.quantity > self.product.inventory.available:
                raise ValueError(
                    f"Insufficient stock. Available: {self.product.inventory.available}"
                )
        super().save(*args, **kwargs)
