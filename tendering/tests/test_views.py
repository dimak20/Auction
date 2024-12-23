from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import timedelta

from tendering.models import Lot, Category, User

ACTIVE_LOTS_URL = reverse("tendering:lot-list-active")
INACTIVE_LOTS_URL = reverse("tendering:lot-list-inactive")
USER_LIST_URL = reverse("tendering:user-list")


class PublicLotsView(TestCase):
    def test_login_required(self):
        res_active_list = self.client.get(ACTIVE_LOTS_URL)
        self.assertNotEqual(res_active_list.status_code, 200)
        res_inactive_list = self.client.get(INACTIVE_LOTS_URL)
        self.assertNotEqual(res_inactive_list.status_code, 200)


class PublicUserView(TestCase):
    def test_login_required(self):
        res = self.client.get(USER_LIST_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivateLotsView(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="test_username", password="test_password"
        )
        self.category = Category.objects.create(name="test_category")
        self.end_date = timezone.now() + timedelta(days=1)
        self.client.force_login(self.user)
        self.lot = Lot.objects.create(
            name="test_1234",
            description="description",
            category=self.category,
            end_date=self.end_date,
            start_price=10,
            owner=self.user,
        )

    def test_retrieve_lots(self):
        Lot.objects.create(
            name="test_12345",
            description="description1",
            category=self.category,
            end_date=self.end_date,
            start_price=10,
            owner=self.user,
        )
        Lot.objects.create(
            name="test_123456",
            description="description11",
            category=self.category,
            end_date=self.end_date,
            start_price=10,
            owner=self.user,
        )
        response = self.client.get(ACTIVE_LOTS_URL)
        self.assertEqual(response.status_code, 200)
        lots = Lot.objects.all()
        self.assertEqual(list(response.context["active_lot_list"]), list(lots))
        self.assertTemplateUsed(response, "tendering/active_list.html")

    def retrieve_lot_detail(self):
        lot = Lot.objects.create(
            id=100,
            name="test_name",
            description="description_test",
            category=self.category,
            end_date=self.end_date,
            start_price=20,
            owner=self.user,
        )
        response = self.client.get(reverse("tendering:lot-detail", args=[100]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["lot"], lot)

    def test_search_lot(self):
        lots = [
            Lot(
                name=f"list_test{i}",
                description=f"test_description{i}",
                category=self.category,
                end_date=self.end_date,
                start_price=f"{i + 5}",
                owner=self.user,
            )
            for i in range(20)
        ]
        lots.extend(
            [
                Lot(
                    name=f"lt_test{i}",
                    description=f"test_description{i}",
                    category=self.category,
                    end_date=self.end_date,
                    start_price=f"{i + 5}",
                    owner=self.user,
                )
                for i in range(20)
            ]
        )
        Lot.objects.bulk_create(lots)
        filter_name = "list"
        filtered_lots = Lot.objects.filter(name__icontains=filter_name)[:5]
        response = self.client.get(ACTIVE_LOTS_URL + f"?name={filter_name}")
        self.assertEqual(
            list(response.context_data["active_lot_list"]), list(filtered_lots)
        )

    def test_lot_pagination(self):
        lots = [
            Lot(
                name=f"list_test{i}",
                description=f"test_description{i}",
                category=self.category,
                end_date=self.end_date,
                start_price=f"{i + 5}",
                owner=self.user,
            )
            for i in range(20)
        ]
        Lot.objects.bulk_create(lots)
        pagination_number = 5
        response = self.client.get(ACTIVE_LOTS_URL + "?page=2")
        paginated_lots = list(Lot.objects.all()[pagination_number:10])
        self.assertEqual(list(response.context_data["active_lot_list"]), paginated_lots)

    def test_update_lot(self):
        payload = {
            "description": "new description",
            "end_date": timezone.now() + timedelta(days=1),
        }
        self.client.post(
            reverse("tendering:lot-update", args=[self.lot.pk]), data=payload
        )
        lot = Lot.objects.get(pk=self.lot.pk)
        self.assertEqual(lot.description, payload.get("description"))
        self.assertEqual(lot.end_date, payload.get("end_date"))


class PrivateUserView(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_username_username", password="test_password"
        )
        self.client.force_login(self.user)

    def test_retrieve_users(self):
        get_user_model().objects.create_user(
            username="username_retrieve_1", password="password"
        )
        get_user_model().objects.create_user(
            username="username_retrieve_2", password="password"
        )
        response = self.client.get(USER_LIST_URL)
        self.assertEqual(response.status_code, 200)
        users = get_user_model().objects.all()
        users_model = User.objects.all()
        self.assertEqual(list(response.context["user_list"]), list(users))
        self.assertEqual(list(response.context["user_list"]), list(users_model))
        self.assertTemplateUsed(response, "tendering/tables.html")

    def test_retrieve_user_detail(self):
        user = get_user_model().objects.create_user(
            id=10, username="username_test_details", password="password"
        )
        response = self.client.get(reverse("tendering:user-detail", args=[10]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"], user)
        self.assertTemplateUsed(response, "pages/profile.html")
