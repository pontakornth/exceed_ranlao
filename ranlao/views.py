from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from http import HTTPStatus

from .models import Table
from .serializers import TableSerializer


# Create your views here.
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def call_staff(request, table_number):
    """
    Call the staff to come to the table
    """
    # TODO: Add auth
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
    # TODO: Add auth
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
    # TODO: Implement
    return None


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def customer_leave(request):
    """
    Decrease customer for this hour.

    This view is only called from hardware.
    """
    # TODO: Implement
    return None
