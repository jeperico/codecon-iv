from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Q

from utils.models import BaseModel


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


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
  name = models.CharField(max_length=255)
  email = models.EmailField(unique=True)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)

  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name']

  class Meta:
    swappable = 'AUTH_USER_MODEL'

  def __str__(self):
    return self.name


class Queue(BaseModel):
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True, default='')

  def __str__(self):
    return self.name


class QueueUser(BaseModel):
  position = models.PositiveIntegerField()
  user = models.ForeignKey(User, related_name='queue_users', on_delete=models.CASCADE)
  queue = models.ForeignKey(Queue, related_name='queue_users', on_delete=models.CASCADE)

  class Meta:
    ordering = ['position']
    constraints = [
      models.UniqueConstraint(fields=['user', 'queue'], name='unique_user_per_queue'),
      models.UniqueConstraint(fields=['queue', 'position'], name='unique_position_per_queue'),
    ]

  def __str__(self):
    return f'{self.user} @ {self.queue} (#{self.position})'


class BookOffer(BaseModel):
  queue_user = models.ForeignKey(
    QueueUser, related_name='book_offers', on_delete=models.SET_NULL, null=True, blank=True,
  )
  seller = models.ForeignKey(User, related_name='offers_sold', on_delete=models.PROTECT)
  buyer = models.ForeignKey(
    User, related_name='offers_bought', on_delete=models.PROTECT, null=True, blank=True,
  )
  queue = models.ForeignKey(Queue, related_name='offers', on_delete=models.PROTECT, null=True)
  sold = models.BooleanField(default=False)
  price = models.PositiveIntegerField()

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['queue_user'],
        condition=Q(sold=False),
        name='unique_active_offer_per_queue_user',
      ),
    ]

  def __str__(self):
    return f'Offer {self.id} ({"sold" if self.sold else "active"})'
