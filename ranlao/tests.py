import datetime
from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from freezegun import freeze_time

# Create your tests here.
from ranlao.models import Table


class TableViewTest(APITestCase):
    def setUp(self) -> None:
        """
        Create the table for testing.

        I set is_calling to False although it is already a default value.
        """
        self.table = Table.objects.create(table_number=1, is_calling=False)
        self.user = User.objects.create_user(username="bad", password="BadPassword123")
        self.call_staff_url = reverse('call_staff', args=[self.table.table_number])
        self.complete_order_url = reverse('complete_order', args=[self.table.table_number])

    def test_call_staff_with_auth(self):
        """Calling staff works when authenticated."""
        self.client.login(username=self.user, password="BadPassword123")
        response = self.client.post(self.call_staff_url)
        # Refresh from DB is required as we mutated it.
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.table.refresh_from_db()
        self.assertTrue(self.table.is_calling)

    def test_call_staff_no_auth(self):
        """Attempt to call staff without login fails."""
        response = self.client.post(self.call_staff_url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.table.refresh_from_db()
        self.assertFalse(self.table.is_calling)

    def test_complete_order_with_auth(self):
        """Complete order works when authenticated."""
        self.client.login(username=self.user, password="BadPassword123")
        self.client.post(self.complete_order_url)
        self.table.refresh_from_db()
        # Cannot set calling status.
        self.assertFalse(self.table.is_calling)

    def test_complete_order_no_auth(self):
        """Attempt to complete order without login fails."""
        response = self.client.post(self.complete_order_url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


class CountingViewTest(APITestCase):
    """Test cases for testing counting customer correctly."""
    def setUp(self) -> None:
        """Authenticate the hardware and setup time."""
        self.user = User.objects.create_user(username="bad", password="BadPassword123")
        self.client.login(username="bad", password="BadPassword123")
        self.enter_url = reverse('enter')
        self.leave_url = reverse('leave')

    def test_enter_only(self):
        """The view counts customer correctly when no one leaves."""
        with freeze_time(datetime.datetime(2020, 12, 18, 18, 0, 0)) as frozen_time:
            for _ in range(5):
                self.client.post(self.enter_url)
                # Simulate not everyone enter at the same time.
                frozen_time.tick(delta=datetime.timedelta(minutes=2))
            response = self.client.get(reverse('count'))
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.data['amount'], 5)
            frozen_time.tick(delta=datetime.timedelta(hours=1))
            self.client.post(self.enter_url)
            response = self.client.get(reverse('count'))
            # The count is valid even the hour is different.
            self.assertEqual(response.data['amount'], 6)

    def test_enter_and_exit(self):
        """The view counts customer correctly when someone leaves."""
        with freeze_time(datetime.datetime(2020, 12, 18, 19, 0, 0)) as frozen_time:
            self.client.post(self.enter_url)
            self.client.post(self.leave_url)
            response = self.client.get(reverse('count'))
            self.assertEqual(response.data['amount'], 0)
            self.client.post(self.enter_url)
            frozen_time.tick(delta=datetime.timedelta(hours=3))
            self.client.post(self.leave_url)
            self.assertEqual(response.data['amount'], 1)

    def test_exit_only(self):
        """
        The view does not acknowledge leaving after zero customer.

        This tests the case that the hardware somehow send leave request
        after there is no customer. It is scary.
        """
        with freeze_time(datetime.datetime(2021, 12, 18, 19, 0, 0)) as frozen_time:
            self.client.post(self.leave_url)
            response = self.client.get(reverse('count'))
            self.assertEqual(response.data['amount'], 0)

