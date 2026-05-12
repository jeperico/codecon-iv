from apps.profiles import api
from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()
router.register('user', api.UserViewSet)
router.register('queue', api.QueueViewSet)
router.register('queue_user', api.QueueUserViewSet)
router.register('book_offer', api.BookOfferViewSet)

router.register(
  'register-user',
  api.UserRegisterView,
  basename='register-user'
)

urlpatterns = [
    path('', include(router.urls)),
]

