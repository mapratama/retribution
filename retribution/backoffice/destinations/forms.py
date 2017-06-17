from django import forms

from retribution.apps.destinations.models import Destination


class BaseDestinationForm(forms.ModelForm):

    class Meta:
        model = Destination
        fields = ('name', 'address', 'description', 'lat', 'long')
