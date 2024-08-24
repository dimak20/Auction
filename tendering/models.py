from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=63)

    class Meta:
        ordering = ("name", )

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Meta:
        ordering = ("username", )

    def __str__(self):
        return f"{self.username}: {self.first_name} {self.last_name}"


class Comment(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    lot = models.ForeignKey("Lot", on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1000)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_time", )


class Lot(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="lots")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    participant = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="active_lots")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lots")

    class Meta:
        ordering = ("is_active", "-start_date")
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["start_date"]),
        ]

    def __str__(self):
        active = "Active" if self.is_active else "Inactive"
        return f"Lot: {self.name}. Owner: {self.owner}. Status: {active}"