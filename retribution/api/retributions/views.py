from datetime import datetime

import pytz

from retribution.api.views import RetributionAPIView
from retribution.apps.retributions.models import Retribution

from rest_framework import status
from rest_framework.response import Response


class Add(RetributionAPIView):
    def post(self, request):
        retributions = request.data.get('retributions')
        # for retribution in retributions:
        #     try:
        #         value = float(retribution['created'])
        #     except ValueError:
        #         continue

        #     created_time = datetime.utcfromtimestamp(value)
        #     created_time = created_time.replace(tzinfo=pytz.utc)

        #     Retribution.objects.update_or_create(
        #         id=retribution['id'],
        #         defaults={
        #             'destination_id': retribution['destination'],
        #             'qr_code': retribution['qr_code'],
        #             'type': retribution['type'],
        #             'quantity': retribution['quantity'],
        #             'price': retribution['price'],
        #             'created_by_id': retribution['created_by'],
        #             'created': created_time,
        #             'transport': retribution['transport'],
        #             'transport_id': retribution['transport_id'],
        #             'mobile_number': retribution['mobile_number'],
        #             'email': retribution['email'],
        #         }
        #     )

        return Response({'status': 'oke'}, status=status.HTTP_200_OK)
