from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from . import services
from .models import BookOffer, Queue, QueueUser, User
from .serializers import (
  BookOfferCreateSerializer,
  BookOfferSerializer,
  ProfileTokenObtainPairSerializer,
  QueueSerializer,
  QueueUserSerializer,
  UserRegisterSerializer,
  UserSerializer,
)


class UserViewSet(
  mixins.RetrieveModelMixin,
  mixins.ListModelMixin,
  viewsets.GenericViewSet,
):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  search_fields = ['name', 'email']

  @action(detail=False, methods=['get'])
  def me(self, request):
    serializer = self.get_serializer(request.user)
    return Response(serializer.data)


class UserRegisterView(mixins.CreateModelMixin, viewsets.GenericViewSet):
  queryset = User.objects.all()
  serializer_class = UserRegisterSerializer
  permission_classes = [permissions.AllowAny]
  authentication_classes = []


class ProfileTokenObtainPairView(TokenObtainPairView):
  serializer_class = ProfileTokenObtainPairSerializer


class QueueViewSet(viewsets.ModelViewSet):
  queryset = Queue.objects.all()
  serializer_class = QueueSerializer

  @action(detail=True, methods=['post'])
  def enter(self, request, pk=None):
    queue = self.get_object()
    queue_user = services.enter_queue(queue=queue, user=request.user)
    return Response(QueueUserSerializer(queue_user).data, status=status.HTTP_201_CREATED)


class QueueUserViewSet(
  mixins.RetrieveModelMixin,
  mixins.ListModelMixin,
  viewsets.GenericViewSet,
):
  queryset = QueueUser.objects.select_related('user', 'queue').all()
  serializer_class = QueueUserSerializer


class BookOfferViewSet(
  mixins.CreateModelMixin,
  mixins.RetrieveModelMixin,
  mixins.ListModelMixin,
  viewsets.GenericViewSet,
):
  queryset = BookOffer.objects.select_related(
    'queue_user__user', 'queue_user__queue', 'queue', 'seller', 'buyer',
  ).all()
  serializer_class = BookOfferSerializer

  def get_queryset(self):
    qs = super().get_queryset()
    sold = self.request.query_params.get('sold')
    queue_id = self.request.query_params.get('queue')
    if sold is not None:
      qs = qs.filter(sold=sold.lower() in ('true', '1'))
    if queue_id:
      qs = qs.filter(queue_id=queue_id)
    return qs

  def create(self, request, *args, **kwargs):
    serializer = BookOfferCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    offer = services.create_offer(
      queue=serializer.validated_data['queue'],
      user=request.user,
      price=serializer.validated_data['price'],
    )
    return Response(BookOfferSerializer(offer).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['post'])
  def buy(self, request, pk=None):
    offer = self.get_object()
    queue_user = services.buy_offer(offer=offer, buyer=request.user)
    return Response(QueueUserSerializer(queue_user).data, status=status.HTTP_200_OK)
