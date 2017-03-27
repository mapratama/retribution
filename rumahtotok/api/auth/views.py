from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import login, logout

from rumahtotok.api.response import ErrorResponse
from rumahtotok.api.views import RumahtotokAPIView, SessionAPIView
from rumahtotok.apps.orders.models import Order
from rumahtotok.core.serializers import (serialize_order, serialize_user)

from rumahtotok.core.utils import force_login

from .forms import RegisterForm, LoginForm, GetConfirmationCodeForm, ResetPasswordForm


class Login(RumahtotokAPIView):

    def post(self, request):
        form = LoginForm(data=request.data)
        if form.is_valid():
            login(request, form.get_user())
            user = form.save()

            if not request.session.session_key:
                request.session.create()

            response = {
                'session_key': request.session.session_key,
                'user': serialize_user(user),
                'orders': [serialize_order(order) for order in
                           user.orders.filter(status__lt=Order.STATUS.completed)]
            }

            return Response(response, status=status.HTTP_200_OK)

        return ErrorResponse(form=form)


class Register(RumahtotokAPIView):

    def post(self, request):
        form = RegisterForm(data=request.data)
        if form.is_valid():
            user = form.save()
            force_login(request, user)

            if not request.session.session_key:
                request.session.create()

            response = {
                'session_key': request.session.session_key,
                'user': serialize_user(user)
            }

            return Response(response, status=status.HTTP_200_OK)
        return ErrorResponse(form=form)


class Logout(SessionAPIView):

    def post(self, request):
        user = request.user
        user.gcm_key = ""
        user.save()

        logout(request)

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class GetConfirmationCode(RumahtotokAPIView):

    def post(self, request):
        form = GetConfirmationCodeForm(data=request.data)
        if form.is_valid():
            form.send_confirmation_code()
            response = {
                'mobile_number': form.cleaned_data['mobile_number']
            }
            return Response(response, status=status.HTTP_200_OK)

        return ErrorResponse(form=form)


class ResetPassword(RumahtotokAPIView):

    def post(self, request):
        form = ResetPasswordForm(data=request.data)
        if form.is_valid():
            form.save()
            return Response({'status': 'oke'}, status=status.HTTP_200_OK)

        return ErrorResponse(form=form)
