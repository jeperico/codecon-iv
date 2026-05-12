from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Queue, QueueUser, BookOffer
from .serializers import (
  QueueSerializer,
  QueueUserSerializer,
  BookOfferSerializer,
  UserSerializer,
  UserRegisterSerializer,
  ProfileTokenObtainPairSerializer,
)

from rest_framework import (
  generics,
  mixins,
  permissions,
  response,
  status,
  views,
  viewsets,
)


class UserViewSet(
  mixins.RetrieveModelMixin,
  mixins.UpdateModelMixin,
  mixins.DestroyModelMixin,
  mixins.ListModelMixin,
  viewsets.GenericViewSet,
):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  search_fields = ['name', 'email']
  
  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = UserSerializer(instance)
    return Response(serializer.data)

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = UserSerializer(instance, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
  

class UserRegisterView(
  mixins.CreateModelMixin,
  viewsets.GenericViewSet,
):
  queryset = User.objects.all()
  serializer_class = UserRegisterSerializer
  permission_classes = [permissions.AllowAny]
  
  def perform_create(self, serializer):
    return super().perform_create(serializer)


class ProfileTokenObtainPairView(TokenObtainPairView):
  serializer_class = ProfileTokenObtainPairSerializer

class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer

    def get_queryset(self):
        return self.queryset.all()
    
class QueueUserViewSet(viewsets.ModelViewSet):
    queryset = QueueUser.objects.all()
    serializer_class = QueueUserSerializer

    def get_queryset(self):
        return self.queryset.all()
    
class BookOfferViewSet(viewsets.ModelViewSet):
    queryset = BookOffer.objects.all()
    serializer_class = BookOfferSerializer

    def get_queryset(self):
        return self.queryset.all()