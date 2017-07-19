from retribution.api.response import ErrorResponse
from retribution.api.views import RetributionAPIView

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

from rest_framework import status
from rest_framework.response import Response


class Login(RetributionAPIView):

    def post(self, request):
        form = AuthenticationForm(data=request.data)
        if form.is_valid():
            login(request, form.get_user())
            user = request.user

            response = {
                "user": {
                    "username": user.username,
                    "password": user.password,
                    "name": user.name or None,
                    "email": user.email or None,
                    "mobile_number": user.mobile_number or None,
                }
            }

            destinations = user.destinations.all()
            destinations_data = []
            for destination in destinations:
                data = {
                    "name": destination.name,
                    "address": destination.address,
                    "people_cost": destination.people_cost,
                    "motor_cost": destination.motor_cost,
                    "sedan_cost": destination.sedan_cost,
                    "mini_bus_cost": destination.mini_bus_cost,
                    "micro_bus_cost": destination.micro_bus_cost,
                    "bus_cost": destination.bus_cost
                }

                destinations_data.append(data)

            response['destinations'] = destinations_data

            return Response(response, status=status.HTTP_200_OK)
        return ErrorResponse(form=form)
