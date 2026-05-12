from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

class UserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
      raise ValueError('The Email field must be set')
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
  id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
  )
  name = models.CharField(max_length=255)
  email = models.EmailField(unique=True)
  created_at = models.DateTimeField(
    auto_now_add=True,
    editable=False,
  )
  updated_at = models.DateTimeField(
    auto_now=True,
  )
  password = models.CharField(max_length=128, default='defaultpassword')
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)

  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name']

  class Meta:
      swappable = "AUTH_USER_MODEL"

  def __str__(self):
      return self.name
