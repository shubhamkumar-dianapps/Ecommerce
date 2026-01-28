from django.contrib.auth.models import BaseUserManager
import phonenumbers


class UserManager(BaseUserManager):
    def _normalize_phone(self, phone):
        """
        Normalize phone number to E164 format if possible.
        Falls back to original value if parsing fails.
        """
        try:
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
        except phonenumbers.NumberParseException:
            pass
        return phone

    def create_user(self, email, phone, role, password=None):
        if not email:
            raise ValueError("Email is required")

        # Normalize email (lowercase) and phone (E164 format)
        email = self.normalize_email(email).lower()
        phone = self._normalize_phone(phone)

        user = self.model(email=email, phone=phone, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, role, password=None):
        user = self.create_user(email=email, phone=phone, role=role, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.email_verified = True  # Auto-verify superuser email
        user.save()
        return user
