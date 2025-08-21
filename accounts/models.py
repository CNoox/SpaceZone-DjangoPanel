from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    national_code = models.CharField(max_length=10, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class VerificationCode(models.Model):
    """
    Stores email verification codes for users (login/register).
    Each request generates a new record.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="verification_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_code():
        return str(secrets.randbelow(1000000)).zfill(6)

    @classmethod
    def create_code_for_user(cls, user, minutes_valid=5):
        code = cls.generate_code()
        instance = cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=minutes_valid)
        )
        return instance
