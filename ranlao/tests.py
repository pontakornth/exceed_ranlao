from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

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
