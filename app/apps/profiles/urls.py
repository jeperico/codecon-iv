from apps.profiles import api
from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()
router.register('user', api.UserViewSet)
router.register(
  'register-user',
  api.UserRegisterView,
  basename='register-user'
)

urlpatterns = [
    path('', include(router.urls)),
]

