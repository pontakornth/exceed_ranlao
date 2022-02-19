import datetime

from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from http import HTTPStatus

from .models import Table, VisitorLog
from .serializers import TableSerializer, LogSerializer


def get_current_time_zero():
    current_time = timezone.now()
    # Set zero
    current_time_zero = current_time.replace(minute=0, second=0, microsecond=0)
    return current_time_zero


def change_log_by_time(time: datetime.datetime, amount: int):
    """Change log by time"""
    # Zero other details after houss
    zero_time = time.replace(minute=0, second=0, microsecond=0)
    current_log, created = VisitorLog.objects.get_or_create(log_time=zero_time)
    # If there is no current log, it is created.
    # The amount will traceback to the previous record if there is any.
    # It will trace up to 6 hours.
    if created:
        maximum_rollback = zero_time - datetime.timedelta(hours=6)
        # Find the previous log upto 6 hours ago.
        previous_log = VisitorLog.objects.filter(log_time__lt=zero_time, log_time__gte=maximum_rollback) \
                                         .order_by('-log_time') \
                                         .first()
        if not previous_log:
            # If there is no previous log, create one for 6 hours ago.
            previous_log = VisitorLog.objects.create(log_time=maximum_rollback)
        else:
        # Create all logs after previous one
        # Set the amount to the same as previous one because there is no signal sent.
        hours_different = zero_time.hour - previous_log.log_time.hour + 1
        VisitorLog.objects.bulk_create(
            [VisitorLog(log_time=zero_time - datetime.timedelta(hours=t), amount=previous_log.amount) for t in
             range(1, hours_different)])
        current_log.amount = previous_log.amount
    # Change if the change makes sense.
    if current_log.amount + amount >= 0:
        current_log.amount += amount
    current_log.save()


# Create your views here.
class TableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


class LogViewSets(viewsets.ReadOnlyModelViewSet):
    queryset = VisitorLog.objects.all().order_by('-log_time')
    serializer_class = LogSerializer


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def call_staff(request, table_number):
    """
    Call the staff to come to the table
    """
    table = get_object_or_404(Table, table_number=table_number)
    table.is_calling = True
    table.save()
    return Response({'message': 'success'}, status=HTTPStatus.OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def complete_order(request, table_number):
    """
    Complete the order customers requested.

    The table will be back to non-calling state.
    """
    table = get_object_or_404(Table, table_number=table_number)
    table.is_calling = False
    table.save()
    return Response({'message': 'success'}, status=HTTPStatus.OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def customer_enter(request):
    """
    Increase customer enter for this hour.

    This view is only called from hardware.
    """
    change_log_by_time(timezone.now(), 1)
    return Response({'message': 'success'})


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def customer_leave(request):
    """
    Decrease customer for this hour.

    This view is only called from hardware.
    """
    change_log_by_time(timezone.now(), -1)
    return Response({'message': 'success'})


@api_view(['GET'])
def get_current_customers(request):
    """Get numbers of current customers."""
    change_log_by_time(timezone.now(), 0)
    current_time_zero = get_current_time_zero()
    current_log, created = VisitorLog.objects.get_or_create(log_time=current_time_zero)
    return Response({'amount': current_log.amount})
