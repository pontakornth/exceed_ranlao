from rest_framework.serializers import ModelSerializer
from .models import Table


class TableSerializer(ModelSerializer):
    class Meta:
        model = Table
        fields = ('table_number', 'is_calling')
