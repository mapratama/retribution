from rest_framework import status
from rest_framework.response import Response

from rumahtotok.api.views import RumahtotokAPIView
from rumahtotok.apps.banners.models import Banner
from rumahtotok.apps.stores.models import Store
from rumahtotok.apps.treatments.models import Treatment
from rumahtotok.core.serializers import (serialize_treatment,
                                         serialize_store,
                                         serialize_banner)


class Home(RumahtotokAPIView):
    def get(self, request):
        treatments = [serialize_treatment(treatment) for treatment in
                      Treatment.objects.all()]
        stores = [serialize_store(store) for store in
                  Store.objects.all()]
        banner = serialize_banner(Banner.objects.last())

        response = {
            "treatments": treatments,
            "stores": stores,
            "banner": banner,
        }

        return Response(response, status=status.HTTP_200_OK)
