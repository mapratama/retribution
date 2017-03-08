from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView


class Created(APIView):

    def get(self, request):
        response = {
			"redemptions": [
				{
					"id": 1,
					"date": "2017-02-23",
					"id_voucher": 3,
					"show_redeem": "yes",
				},
				{
					"id": 2,
					"date": "2017-03-02",
					"id_voucher": 5,
					"show_redeem": "yes",
				}
			]
		}
        return Response(response, status=status.HTTP_200_OK)
