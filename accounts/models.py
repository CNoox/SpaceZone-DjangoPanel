from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets
from rest_framework_simplejwt.tokens import AccessToken


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
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

def user_directory_path(instance, filename):
    return f"{instance.email}/profile/{filename}"

class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    national_code = models.CharField(max_length=10, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self,perm,obj=None):
        return True

    def has_module_perms(self,app_label):
        return True



class UserCodeModel(models.Model):
    user = models.OneToOneField(CustomUserModel, on_delete=models.CASCADE, related_name='usercode')
    code = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    REQUEST_INTERVAL = timedelta(seconds=30)

    def seconds_until_next_code(self):
        if not self.created_at:
            return 0
        remaining = (self.created_at + self.REQUEST_INTERVAL - timezone.now()).total_seconds()
        return max(0, int(remaining))

    def can_request_new(self):
        return timezone.now() >= self.created_at + self.REQUEST_INTERVAL

    def create_code(self):
        if UserCodeModel.DoesNotExist:
            self.code = str(secrets.randbelow(1000000)).zfill(6)
            self.created_at = timezone.now()
            self.expires_at = self.created_at + timedelta(minutes=5)
            self.is_used = False
            self.save()
            return self.code
        if self.can_request_new():
            self.code = str(secrets.randbelow(1000000)).zfill(6)
            self.created_at = timezone.now()
            self.expires_at = self.created_at + timedelta(minutes=5)
            self.is_used = False
            self.save()
            return self.code
        return None
    def expires_code(self):
        if not self.created_at or not self.expires_at:
            return True
        return timezone.now() >= self.expires_at

    def __str__(self):
        return self.user.email


