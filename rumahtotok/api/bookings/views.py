from rest_framework import status
from rest_framework.response import Response

from rumahtotok.api.response import ErrorResponse
from rumahtotok.api.views import SessionAPIView
from rumahtotok.core.serializers import serialize_order, serialize_booking

from .forms import (PreviewBookingForm, BookingCreationForm, EditBookingForm,
                    BookingReviewForm, BookingCancelationForm)


class Preview(SessionAPIView):

    def post(self, request):
        form = PreviewBookingForm(data=request.data, user=request.user)
        if form.is_valid():
            service = form.cleaned_data.get('service')

            # Booking Preview should return balance_used
            balance_used = 0
            if request.user.has_enough_balance(service.correct_price):
                balance_used = service.correct_price

            data = {
                "price": service.correct_price,
                "balance_used": balance_used,
                "amount_to_pay": service.correct_price - balance_used
            }

            return Response(data, status=status.HTTP_200_OK)

        return ErrorResponse(form=form)


class Create(SessionAPIView):

    def post(self, request):
        form = BookingCreationForm(data=request.data, user=request.user)

        if form.is_valid():
            return Response(serialize_order(form.save().order), status=status.HTTP_200_OK)

        return ErrorResponse(form=form)


class Edit(SessionAPIView):

    def post(self, request):
        form = EditBookingForm(data=request.data, user=request.user)

        if form.is_valid():
            return Response(serialize_order(form.save().order), status=status.HTTP_200_OK)

        return ErrorResponse(form=form)


class Review(SessionAPIView):

    def post(self, request):
        form = BookingReviewForm(user=request.user, data=request.data)
        if form.is_valid():
            booking = form.save()
            # send sms to bo pita

            response = {
                'booking': serialize_booking(booking)
            }
            return Response(response, status=status.HTTP_200_OK)
        return ErrorResponse(form=form)


class Cancel(SessionAPIView):
    def post(self, request):
        form = BookingCancelationForm(user=request.user, data=request.data)
        if form.is_valid():
            booking = form.cleaned_data['booking']
            booking.cancel()

            response = {
                'order': serialize_order(booking.order)
            }
            return Response(response, status=status.HTTP_200_OK)
        return ErrorResponse(form=form)
