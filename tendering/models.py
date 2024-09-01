from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=63)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    class Meta:
        ordering = ("username",)

    def __str__(self) -> str:
        return f"{self.username}: {self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("tendering:user-detail", args=[str(self.id)])


class Comment(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    lot = models.ForeignKey("Lot", on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1000)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_time",)

    def __str__(self) -> str:
        return f"{self.owner}: {self.text}. Lot: {self.lot}"


class Lot(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField(max_length=1000)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="lots"
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    participant = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Bid")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lots"
    )
    photo = models.ImageField(upload_to="tenders/", blank=True, null=True)

    class Meta:
        ordering = ("is_active", "-start_date")
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["end_date"]),
        ]

    def __str__(self) -> str:
        active = "Active" if self.is_active else "Inactive"
        return f"Lot: {self.name}. Owner: {self.owner}. Status: {active}"

    def get_highest_bidder(self) -> settings.AUTH_USER_MODEL:
        highest_bid = self.bids.order_by("-amount").first()
        return highest_bid.user if highest_bid else None

    def get_highest_bid_amount(self) -> Decimal:
        highest_bid = self.bids.order_by("-amount").first()
        return highest_bid.amount if highest_bid else None

    def get_absolute_url(self):
        return reverse("tendering:lot-detail", args=[str(self.id)])

    def get_progress_percentage(self):

        start_date = self.start_date
        end_date = self.end_date
        current_date = timezone.now()
        if start_date >= end_date:
            return 100.0 if current_date >= end_date else 0.0
        total_duration = (end_date - start_date).total_seconds()
        elapsed_duration = (current_date - start_date).total_seconds()
        progress = (elapsed_duration / total_duration) * 100
        progress = max(0.0, min(progress, 100.0))
        return round(progress, 2)


class Bid(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("-amount",)

    def __str__(self) -> str:
        return f"User: {self.user} (lot: {self.lot.name}, amount: {self.amount})"
