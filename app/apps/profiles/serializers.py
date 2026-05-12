from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import BookOffer, Queue, QueueUser, User


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'name', 'email', 'is_active', 'is_staff', 'created_at', 'updated_at']
    read_only_fields = fields


class QueueSerializer(serializers.ModelSerializer):
  class Meta:
    model = Queue
    fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class QueueUserSerializer(serializers.ModelSerializer):
  user = UserSerializer(read_only=True)
  queue = QueueSerializer(read_only=True)

  class Meta:
    model = QueueUser
    fields = ['id', 'position', 'user', 'queue', 'created_at', 'updated_at']
    read_only_fields = fields


class BookOfferSerializer(serializers.ModelSerializer):
  queue_user = QueueUserSerializer(read_only=True)
  queue = QueueSerializer(read_only=True)
  seller = UserSerializer(read_only=True)
  buyer = UserSerializer(read_only=True)

  class Meta:
    model = BookOffer
    fields = [
      'id', 'queue', 'queue_user', 'seller', 'buyer',
      'sold', 'price', 'created_at', 'updated_at',
    ]
    read_only_fields = fields


class BookOfferCreateSerializer(serializers.Serializer):
  queue = serializers.PrimaryKeyRelatedField(queryset=Queue.objects.all())
  price = serializers.IntegerField(min_value=1)


class UserRegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(
    write_only=True,
    required=True,
    validators=[validate_password],
  )

  class Meta:
    model = User
    fields = ['id', 'name', 'email', 'password', 'created_at', 'updated_at']
    extra_kwargs = {
      'password': {'write_only': True},
      'id': {'read_only': True},
      'created_at': {'read_only': True},
      'updated_at': {'read_only': True},
    }

  def create(self, validated_data):
    with transaction.atomic():
      password = validated_data.pop('password')
      user = User.objects.create(**validated_data)
      user.set_password(password)
      user.save()
      return user


class ProfileTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    data = super().validate(attrs)
    data['user'] = UserSerializer(self.user).data
    return data
