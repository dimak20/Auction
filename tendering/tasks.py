from celery import shared_task
from django.utils import timezone
from .models import Lot

@shared_task
def close_expired_lots():
    now = timezone.now()
    expired_lots = Lot.objects.filter(is_active=True, end_date__lte=now)
    for lot in expired_lots:
        lot.is_active = False
        highest_bid = lot.bids.order_by('-amount').first()
        if highest_bid:
            lot.owner = highest_bid.user
        lot.save()
