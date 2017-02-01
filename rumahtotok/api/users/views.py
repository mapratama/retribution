from rest_framework import status
from rest_framework.response import Response

from rumahtotok.api.views import SessionAPIView
from rumahtotok.api.response import ErrorResponse
from rumahtotok.core.serializers import serialize_user

from .forms import UpdateProfileForm


class UserDetail(SessionAPIView):
    logging_key = 'userdetail'

    def get(self, request):
        response = serialize_user(request.user)
        return Response(response, status=status.HTTP_200_OK)


class ChangeProfile(SessionAPIView):

    def post(self, request):
        form = UpdateProfileForm(data=request.data)

        if form.is_valid():
            user = form.save(user=request.user)
            response = serialize_user(user)

            return Response(response, status=status.HTTP_200_OK)
        return ErrorResponse(form=form)
