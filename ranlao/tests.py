import datetime
from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from freezegun import freeze_time

# Create your tests here.
from ranlao.models import Table, VisitorLog
from ranlao.views import get_current_time_zero, change_log_by_time


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
            self.client.post(self.leave_url)
            self.client.post(self.enter_url)
            # There is 1 person.
            frozen_time.tick(delta=datetime.timedelta(hours=3))
            self.client.post(self.enter_url)
            response = self.client.get(reverse('count'))
            self.assertEqual(response.data['amount'], 2)

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


class StatisticViewTest(APITestCase):
    """
    Tests for statistic view.

    The store only opens on 18:00 - 24:00.

    Note: This assumes no signal is sent before 18:00
    """

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="table01", password="TableExceed01")
        self.client.login(username="table01", password="TableExceed01")
        self.statistic_url = reverse('statistic')
        self.enter_url = reverse('enter')
        self.leave_url = reverse('leave')

    def test_near_closing(self):
        """Statistic is correct when almost closing."""
        with freeze_time(datetime.datetime(2019, 12, 19, 18, 0, 0, 0)) as frozen_time:
            # 4 for 18:00
            for i in range(4):
                self.client.post(self.enter_url)
            # 5 for 19.00
            print(timezone.now())
            frozen_time.tick(delta=datetime.timedelta(hours=1))
            self.client.post(self.enter_url)
            # 0 for 21.00
            frozen_time.tick(delta=datetime.timedelta(hours=3))
            for i in range(5):
                self.client.post(self.leave_url)
            # There is no customer after 21.00
            frozen_time.tick(delta=datetime.timedelta(hours=3))
            response = self.client.get(self.statistic_url)
            stat = response.data['stat']
            print(stat)
            raw_stat = list(map(lambda x: x.get('amount', 0), stat))
            self.assertEqual(raw_stat, [4, 5, 5, 0, 0, 0])


class ChangeLogByTimeTest(APITestCase):
    """Change this one."""
    def test_previous_log(self):
        """The function works correctly when there is a previous log from the last hour."""
        zero_time = get_current_time_zero()
        previous_log = VisitorLog.objects.create(log_time=zero_time - datetime.timedelta(hours=1), amount=30)
        change_log_by_time(zero_time, 1)
        current_log = VisitorLog.objects.get(log_time=zero_time)
        self.assertEqual(current_log.amount, 31)

    def test_no_previous_log(self):
        """The function works correctly when there is no previous log and it creates logs for previous 6 hours"""
        zero_time = get_current_time_zero()
        change_log_by_time(zero_time, 1)
        for i in range(1, 7):
            previous_log, created = VisitorLog.objects.get_or_create(log_time=zero_time - datetime.timedelta(hours=1))
            if created:
                self.fail("The function does not create previous log.")
            self.assertEqual(previous_log.amount, 0)
        current_log, created = VisitorLog.objects.get_or_create(log_time=zero_time)
        if created:
            self.fail("It should be already there.")
        self.assertEqual(current_log.amount, 1)

    def test_long_previous_log(self):
        """The function works correctly when there is a previous log fewer than 6 hours."""
        zero_time = get_current_time_zero()
        previous_time = zero_time - datetime.timedelta(hours=5)
        previous_log = VisitorLog.objects.create(log_time=previous_time, amount=7)
        change_log_by_time(zero_time, 8)
        for i in range(5, 0, -1):
            previous_time = zero_time - datetime.timedelta(hours=i)
            previous_log, created = VisitorLog.objects.get_or_create(log_time=previous_time)
            if created:
                self.fail("It should be created already. ")
            self.assertEqual(previous_log.amount, 7, msg=f"Fail at hour {i} hours ago")
        current_log, created = VisitorLog.objects.get_or_create(log_time=zero_time)
        if created:
            self.fail("It should be created already.")
        self.assertEqual(current_log.amount, 7 + 8)

