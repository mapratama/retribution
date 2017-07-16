from django import forms

from retribution.apps.destinations.models import Destination


class BaseDestinationForm(forms.ModelForm):

    class Meta:
        model = Destination
        fields = ('name', 'address', 'people_cost', 'motor_cost', 'sedan_cost',
                  'mini_bus_cost', 'micro_bus_cost', 'bus_cost', 'description',
                  'lat', 'long')
