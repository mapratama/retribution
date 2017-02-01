import json

from django.conf import settings
from django.utils import timezone
from django_redis import get_redis_connection
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from .authentication import (JSONTokenAuthentication, SessionAuthentication)
from .exceptions import APIError

from .permissions import IsSecure


class RumahtotokAPIView(APIView):
    permission_classes = (IsSecure,)
    authentication_classes = (JSONTokenAuthentication,)

    renderer_classes = (JSONRenderer,)

    logging_key = None

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # save this first before consumed by DRF-Request
        # Hit the method for API
        response = super(RumahtotokAPIView, self).dispatch(request, *args, **kwargs)

        return response

    def handle_exception(self, exc):
        """ Override the exception handler to handle APIError first
        """
        if isinstance(exc, APIError):
            return Response({'detail': exc.detail}, status=exc.status_code,
                            exception=True)
        return super(RumahtotokAPIView, self).handle_exception(exc)


class SessionAPIView(RumahtotokAPIView):

    authentication_classes = (JSONTokenAuthentication, SessionAuthentication)
