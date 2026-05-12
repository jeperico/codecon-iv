from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from .models import BookOffer, Queue, QueueUser, User


@transaction.atomic
def enter_queue(*, queue: Queue, user: User) -> QueueUser:
  if QueueUser.objects.filter(queue=queue, user=user).exists():
    raise ValidationError({'user': 'User is already in this queue.'})

  last = (
    QueueUser.objects
    .select_for_update()
    .filter(queue=queue)
    .order_by('-position')
    .first()
  )
  next_position = (last.position + 1) if last else 1
  return QueueUser.objects.create(queue=queue, user=user, position=next_position)


@transaction.atomic
def create_offer(*, queue: Queue, user: User, price: int) -> BookOffer:
  if price <= 0:
    raise ValidationError({'price': 'Price must be positive.'})

  try:
    queue_user = QueueUser.objects.get(queue=queue, user=user)
  except QueueUser.DoesNotExist:
    raise ValidationError({'queue': 'You are not in this queue.'})

  if BookOffer.objects.filter(queue_user=queue_user, sold=False).exists():
    raise ValidationError({'queue_user': 'There is already an active offer for this position.'})

  return BookOffer.objects.create(
    queue_user=queue_user,
    seller=user,
    queue=queue,
    price=price,
  )


@transaction.atomic
def buy_offer(*, offer: BookOffer, buyer: User) -> QueueUser:
  offer = BookOffer.objects.select_for_update().get(pk=offer.pk)
  if offer.sold:
    raise ValidationError({'offer': 'This offer has already been sold.'})
  if offer.queue_user_id is None:
    raise ValidationError({'offer': 'This offer is no longer available.'})

  seller_qu = QueueUser.objects.select_for_update().get(pk=offer.queue_user_id)
  queue_id = seller_qu.queue_id
  seller_position = seller_qu.position

  if seller_qu.user_id == buyer.id:
    raise ValidationError({'buyer': 'You cannot buy your own offer.'})

  buyer_qu = (
    QueueUser.objects
    .select_for_update()
    .filter(queue_id=queue_id, user=buyer)
    .first()
  )

  if buyer_qu is None:
    seller_qu.user = buyer
    seller_qu.save(update_fields=['user', 'updated_at'])
    result = seller_qu
  else:
    if buyer_qu.position <= seller_position:
      raise ValidationError({'buyer': 'Buyer is already ahead of (or at) this position.'})

    seller_qu.delete()
    (
      QueueUser.objects
      .filter(queue_id=queue_id, position__gt=seller_position)
      .update(position=F('position') - 1)
    )
    buyer_qu.refresh_from_db()
    result = buyer_qu

  offer.sold = True
  offer.buyer = buyer
  offer.save(update_fields=['sold', 'buyer', 'updated_at'])

  return result
