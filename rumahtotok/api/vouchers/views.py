from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView


class Created(APIView):

    def get(self, request):
        response = {
			"transactions": [
				{
					"id": 78,
					"id_voucher": 1,
					"date": "2016-11-16 05:30:00",
					"type_payment": "pulsa",
					"used": "yes"
				},
				{
					"id": 79,
					"id_voucher": 5,
					"date": "2016-11-15 05:30:00",
					"type_payment": "wallet",
					"used": "no"
				}

			]

		}
        return Response(response, status=status.HTTP_200_OK)
