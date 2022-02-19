from rest_framework.serializers import ModelSerializer
from .models import Table, VisitorLog


class TableSerializer(ModelSerializer):
    class Meta:
        model = Table
        fields = ('table_number', 'is_calling')


class LogSerializer(ModelSerializer):
    class Meta:
        model = VisitorLog
        fields = ('log_time', 'amount')
