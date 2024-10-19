from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from tendering.models import Lot, Category, Comment, Bid


class ModelsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test_username",
            password="test12345",
            first_name="test_first",
            last_name="test_last",
        )
        self.category = Category.objects.create(name="test")
        self.date = timezone.now() + timedelta(days=1)
        self.lot = Lot.objects.create(
            name="test",
            description="test_description",
            category=self.category,
            end_date=self.date,
            start_price=10,
            owner=self.user,
        )

    def test_category_str(self):
        category = Category.objects.create(name="Book")
        self.assertEqual(str(category), category.name)

    def test_user_str(self):
        password = "test12345"
        test_user = get_user_model().objects.create_user(
            username="test_username_test",
            password=password,
            first_name="test_first",
            last_name="test_last",
        )
        self.assertEqual(
            str(test_user),
            f"{test_user.username}: {test_user.first_name} {test_user.last_name}",
        )
        self.assertTrue(test_user.check_password(password))

    def test_comment_str(self):
        comment = Comment.objects.create(
            owner=self.user, lot=self.lot, text="some very long test_text"
        )
        self.assertEqual(
            str(comment), f"{comment.owner}: {comment.text}. " f"Lot: {comment.lot}"
        )

    def test_lot_str(self):
        lot = Lot.objects.create(
            name="testt",
            description="looooong description",
            category=self.category,
            end_date=self.date,
            start_price=22,
            owner=self.user,
        )
        active = "Active" if lot.is_active else "Inactive"
        self.assertEqual(
            str(lot), f"Lot: {lot.name}. Owner: {lot.owner}. Status: {active}"
        )

    def test_bid_str(self):
        bid = Bid.objects.create(lot=self.lot, user=self.user, amount=20)
        self.assertEqual(
            str(bid), f"User: {bid.user} (lot: {bid.lot.name}, amount: {bid.amount})"
        )
