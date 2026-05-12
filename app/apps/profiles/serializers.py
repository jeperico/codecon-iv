from .models import User
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = '__all__'


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
    data["user"] = UserSerializer(self.user).data

    return data
