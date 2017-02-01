from rest_framework import status
from rest_framework.response import Response

from rumahtotok.api.views import RumahtotokAPIView
from rumahtotok.apps.stores.models import Store
from rumahtotok.core.serializers import serialize_store


class StoreList(RumahtotokAPIView):
    def get(self, request):
        response = [serialize_store(store) for store in
                    Store.objects.filter(is_active=True)]
        return Response(response, status=status.HTTP_200_OK)
