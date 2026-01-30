"""
Account Permissions

Custom permission classes for role-based access control.

Note: App-specific permissions are in their respective apps:
- Shopkeeper/Product permissions: apps/products/permissions.py
- Review permissions: apps/reviews/permissions.py
"""

from .base import IsEmailVerified, IsActiveUser
from .admin import IsAdmin, IsAdminOrReadOnly
from .customer import IsCustomer

__all__ = [
    # Base permissions
    "IsEmailVerified",
    "IsActiveUser",
    # Role-based permissions
    "IsAdmin",
    "IsAdminOrReadOnly",
    "IsCustomer",
]
