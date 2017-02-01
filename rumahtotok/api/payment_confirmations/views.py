from rest_framework import status
from rest_framework.response import Response

from rumahtotok.api.response import ErrorResponse
from rumahtotok.api.views import SessionAPIView
from rumahtotok.apps.orders.models import PaymentConfirmation
from rumahtotok.core.serializers import serialize_payment_confirmation
from .forms import PaymentSerializer


class Add(SessionAPIView):
    serializer_class = PaymentSerializer

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            return Response(serialize_payment_confirmation(payment), status=status.HTTP_201_CREATED)
        return ErrorResponse(serializer=serializer)


class Details(SessionAPIView):
    def get(self, request, id):
        try:
            payment = PaymentConfirmation.objects.get(id=id, order__user_id=request.user.id)
        except PaymentConfirmation.DoesNotExist:
            return ErrorResponse(error_description='Payment Not Found')

        response = serialize_payment_confirmation(payment)
        return Response(response, status=status.HTTP_200_OK)
