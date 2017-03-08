from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView


class Created(APIView):

    def get(self, request):
        response = {
			"wallets": [
				{
					"id": 1,
					"nomor": "1234567ABCDE",
					"amount": 50000,
					"id_bank": 1,
					"metode": "atm",
					"type": "deposit",
					"status": "pending",
					"remark": "test",
					"balance": 10000,
					"date": "2016-12-15 07:30:00",
				},
				{
					"id": 2,
					"nomor": "789789FGHUJK",
					"amount": 20000,
					"id_bank": 1,
					"metode": "atm",
					"type": "withdraw",
					"status": "approve",
					"remark": "test",
					"balance": 10000,
					"date": "2016-12-15 07:30:00",
				}
			]
		}
        return Response(response, status=status.HTTP_200_OK)
