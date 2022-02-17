from django.urls import reverse
from rest_framework.test import APITestCase

# Create your tests here.
from ranlao.models import Table


class TableViewTest(APITestCase):
    def setUp(self) -> None:
        self.table = Table.objects.create(table_number=1)

    def test_call_staff(self):
        url = reverse('call_staff', args=[1])
        self.client.post(url)
        # Refresh from DB is required as we mutated it.
        self.table.refresh_from_db()
        self.assertTrue(self.table.is_calling)

    def test_complete_order(self):
        url = reverse('complete_order', args=[1])
        self.client.post(url)
        self.table.refresh_from_db()
        self.assertFalse(self.table.is_calling)
