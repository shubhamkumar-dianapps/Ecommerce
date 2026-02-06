from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User, AdminProfile, ShopKeeperProfile, CustomerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create the appropriate profile when a new user is created.

    Note: We use .create() instead of .get_or_create() since this only runs
    when created=True, ensuring we only create the profile once.
    """
    if kwargs.get("raw"):
        return

    if created:
        if instance.role == User.Role.ADMIN:
            AdminProfile.objects.create(user=instance)
        elif instance.role == User.Role.SHOPKEEPER:
            ShopKeeperProfile.objects.create(user=instance)
        elif instance.role == User.Role.CUSTOMER:
            CustomerProfile.objects.create(user=instance)
