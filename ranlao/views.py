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
from .serializers import TableSerializer


def get_current_time_zero():
    current_time = timezone.now()
    # Set zero
    current_time_zero = current_time.replace(minute=0, second=0, microsecond=0)
    return current_time_zero


# Create your views here.
class TableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


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
    current_time_zero = get_current_time_zero()
    current_log, _ = VisitorLog.objects.get_or_create(log_time=current_time_zero)
    current_log.amount += 1
    current_log.save()
    return Response({'message': 'success'})


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def customer_leave(request):
    """
    Decrease customer for this hour.

    This view is only called from hardware.
    """
    current_time_zero = get_current_time_zero()
    current_log, _ = VisitorLog.objects.get_or_create(log_time=current_time_zero)
    if current_log.amount > 0:
        current_log.amount -= 1
    current_log.save()
    return Response({'message': 'success'})


@api_view(['GET'])
def get_current_customers(request):
    """Get numbers of current customers."""
    current_time_zero = get_current_time_zero()
    current_log, _ = VisitorLog.objects.get_or_create(log_time=current_time_zero)
    return Response({'amount': current_log.amount})
