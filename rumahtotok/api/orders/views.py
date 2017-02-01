from rest_framework import status
from rest_framework.response import Response

from rumahtotok.apps.orders.models import Order
from rumahtotok.api.response import ErrorResponse
from rumahtotok.api.views import SessionAPIView
from rumahtotok.core.serializers import serialize_order

from .forms import ValidatePromotionCodeForm, OrderCreationForm, OrderCancelationForm


class OrderList(SessionAPIView):
    def get(self, request):
        response = [serialize_order(order) for order in
                    request.user.orders.filter(status__lt=Order.STATUS.completed)]
        return Response(response, status=status.HTTP_200_OK)


class Create(SessionAPIView):

    def post(self, request):
        form = OrderCreationForm(data=request.data, user=request.user)
        if form.is_valid():
            return Response(serialize_order(form.save()), status=status.HTTP_200_OK)

        return ErrorResponse(form=form)


class OrderDetail(SessionAPIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user_id=request.user.id)
        except Order.DoesNotExist:
            return ErrorResponse(error_description='Order Not Found')

        response = {
            'order': serialize_order(order)
        }
        return Response(response, status=status.HTTP_200_OK)


class Cancel(SessionAPIView):
    def post(self, request):
        user = request.user
        form = OrderCancelationForm(user=user, data=request.data)
        if form.is_valid():
            order = form.cleaned_data['order']
            order.cancel(user)

            response = {
                'order': serialize_order(order)
            }
            return Response(response, status=status.HTTP_200_OK)
        return ErrorResponse(form=form)


class ValidatePromotion(SessionAPIView):

    def post(self, request):
        form = ValidatePromotionCodeForm(data=request.data, user=request.user)
        if form.is_valid():
            service = form.cleaned_data.get('service')

            promotion = form.promotion
            discount = promotion.calculate_discount(service.correct_price)
            discounted_price = service.correct_price - discount

            balance_used = 0
            if request.user.has_enough_balance(discounted_price):
                balance_used = discounted_price

            response = {
                "price": service.correct_price,
                "discount": discount,
                "balance_used": balance_used,
                "amount_to_pay": discounted_price - balance_used
            }

            return Response(response, status=status.HTTP_200_OK)

        return ErrorResponse(form=form)
