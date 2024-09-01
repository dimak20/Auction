from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="super_username",
            password="super_password1234"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create(
            username="username",
            password="password",
            phone_number="380999999999",
            location="test_location"
        )

    def test_user_location_listed(self):
        url = reverse("admin:tendering_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.location)

    def test_user_phone_number_listed(self):
        url = reverse("admin:tendering_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.phone_number)

    def test_user_detail_location_listed(self):
        url = reverse("admin:tendering_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertContains(res, self.user.location)

    def test_user_detail_phone_number_listed(self):
        url = reverse("admin:tendering_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertContains(res, self.user.phone_number)
