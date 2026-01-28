import uuid
from django.db import models
from .user import User
from apps.common.models import TimeStampedModel


class AdminProfile(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
