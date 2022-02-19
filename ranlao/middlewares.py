from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from ranlao.models import UserTable


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # This is custom.
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            table = UserTable.objects.get(user=user)
        except UserTable.DoesNotExist:
            table = None
        token, created = Token.objects.get_or_create(user=user)
        is_staff = user.is_staff
        return Response({
            'token': token.key,
            'table': table.table.table_number if table else None,
            'is_staff': user.is_staff,
        })
