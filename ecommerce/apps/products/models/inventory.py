from django.db import models, transaction
from apps.products.models.product import Product


class Inventory(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="inventory"
    )
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)  # Items in pending orders
    low_stock_threshold = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - Stock: {self.available}"

    @property
    def available(self):
        """Available stock = total quantity - reserved"""
        return max(0, self.quantity - self.reserved)

    @property
    def is_low_stock(self):
        return self.available <= self.low_stock_threshold

    @property
    def is_in_stock(self):
        return self.available > 0

    def reserve(self, quantity: int) -> bool:
        """
        Reserve stock for an order with database-level locking.

        Uses select_for_update to prevent race conditions when
        multiple requests try to reserve the same inventory.

        Args:
            quantity: Number of items to reserve

        Returns:
            bool: True if reservation successful, False if insufficient stock
        """
        with transaction.atomic():
            # Lock this row until transaction completes
            locked_inventory = Inventory.objects.select_for_update().get(pk=self.pk)

            if locked_inventory.available >= quantity:
                locked_inventory.reserved += quantity
                locked_inventory.save(update_fields=["reserved"])
                # Update self to reflect current state
                self.reserved = locked_inventory.reserved
                return True
            return False

    def release(self, quantity: int) -> None:
        """
        Release reserved stock with database-level locking.

        Args:
            quantity: Number of items to release
        """
        with transaction.atomic():
            locked_inventory = Inventory.objects.select_for_update().get(pk=self.pk)
            locked_inventory.reserved = max(0, locked_inventory.reserved - quantity)
            locked_inventory.save(update_fields=["reserved"])
            self.reserved = locked_inventory.reserved

    def confirm_reservation(self, quantity: int) -> None:
        """
        Convert reserved stock to sold (subtract from both quantity and reserved).

        Called when order is confirmed/paid.

        Args:
            quantity: Number of items sold
        """
        with transaction.atomic():
            locked_inventory = Inventory.objects.select_for_update().get(pk=self.pk)
            locked_inventory.quantity -= quantity
            locked_inventory.reserved -= quantity
            locked_inventory.save(update_fields=["quantity", "reserved"])
            self.quantity = locked_inventory.quantity
            self.reserved = locked_inventory.reserved

    def adjust_stock(self, quantity: int) -> None:
        """
        Adjust total stock quantity with database-level locking.

        Args:
            quantity: Amount to adjust (positive to add, negative to subtract)
        """
        with transaction.atomic():
            locked_inventory = Inventory.objects.select_for_update().get(pk=self.pk)
            locked_inventory.quantity += quantity
            locked_inventory.save(update_fields=["quantity"])
            self.quantity = locked_inventory.quantity
