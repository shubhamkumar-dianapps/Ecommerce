import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.accounts.managers import UserManager
from apps.accounts.validators import validate_phone_number
from apps.common.models import TimeStampedModel
from apps.common import constants


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SHOPKEEPER = "SHOPKEEPER", "ShopKeeper"
        CUSTOMER = "CUSTOMER", "Customer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(
        max_length=constants.PHONE_MAX_LENGTH,
        unique=True,
        validators=[validate_phone_number],
        db_index=True,
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    email_verified = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "role"]

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_shopkeeper(self):
        return self.role == self.Role.SHOPKEEPER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER
