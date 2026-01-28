from django.db import models
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

    def reserve(self, quantity):
        """Reserve stock for an order"""
        if self.available >= quantity:
            self.reserved += quantity
            self.save()
            return True
        return False

    def release(self, quantity):
        """Release reserved stock"""
        self.reserved = max(0, self.reserved - quantity)
        self.save()

    def adjust_stock(self, quantity):
        """Adjust total stock quantity"""
        self.quantity += quantity
        self.save()
