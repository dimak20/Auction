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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    lot = models.ForeignKey("Lot", on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1000)
