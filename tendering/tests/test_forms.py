from datetime import timedelta
from decimal import Decimal
from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tendering.forms import LotForm, BidForm
from tendering.models import Lot, Category, User, Comment, Bid


class FormsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_username_forms",
            password="test_password"
        )
        self.category = Category.objects.create(name="name")
        self.client.force_login(self.user)
        self.lot = Lot.objects.create(
            name="name_123",
            description="description123",
            category=self.category,
            end_date=timezone.now() + timedelta(days=1),
            start_price=Decimal(20),
            owner=self.user
        )

    def test_create_lot(self):
        form_data = {
            "name": "test_name",
            "description": "test_description",
            "category": self.category.id,
            "end_date": timezone.now() + timedelta(days=1),
            "start_price": Decimal(10),
            "owner": self.user.id
        }
        form = LotForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.client.post(reverse("tendering:lot-create"), data=form_data)
        new_lot = Lot.objects.get(name=form_data["name"])
        self.assertEqual(new_lot.name, form_data["name"])
        self.assertEqual(new_lot.description, form_data["description"])
        self.assertEqual(new_lot.category.id, form_data["category"])
        self.assertEqual(new_lot.end_date, form_data["end_date"])
        self.assertEqual(new_lot.start_price, form_data["start_price"])
        self.assertEqual(new_lot.owner.id, form_data["owner"])

    def test_create_bid(self):
        form_data = {
            "lot": self.lot.id,
            "user": self.user.id,
            "amount": Decimal(30)
        }
        form_data_invalid = {
            "lot": self.lot.id,
            "user": self.user.id,
            "amount": Decimal(1)
        }
        form = BidForm(data=form_data)
        invalid_form = BidForm(data=form_data_invalid)
        self.assertTrue(form.is_valid())
        self.assertFalse(invalid_form.full_clean())
