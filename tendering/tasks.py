from background_task import background
from django.utils import timezone
from .models import Lot


@background(schedule=300)
def close_expired_lots():
    now = timezone.now()
    expired_lots = Lot.objects.filter(is_active=True, end_date__lte=now)
    for lot in expired_lots:
        lot.is_active = False
        highest_bid = lot.bids.order_by('-amount').first()
        if highest_bid:
            lot.owner = highest_bid.user
        lot.save()
