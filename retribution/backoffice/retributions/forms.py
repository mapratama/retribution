from django import forms

from retribution.apps.destinations.models import Destination
from retribution.apps.retributions.models import Retribution


class BaseRetributionForm(forms.ModelForm):

    class Meta:
        model = Retribution
        fields = ('destination', 'type', 'quantity', 'transport', 'transport_id', 'mobile_number')

    def save(self, user, *args, **kwargs):
        kwargs['commit'] = False
        retribution = super(BaseRetributionForm, self).save(*args, **kwargs)
        retribution.created_by = user

        price = retribution.quantity * 2500
        if retribution.transport == Retribution.TRANSPORT.motor:
            price = price + 8000
        elif retribution.transport == Retribution.TRANSPORT.sedan:
            price = price + 20000
        elif retribution.transport == Retribution.TRANSPORT.mini_bus:
            price = price + 30000
        elif retribution.transport == Retribution.TRANSPORT.micro_bus:
            price = price + 70000
        elif retribution.transport == Retribution.TRANSPORT.bus:
            price = price + 135000

        retribution.price = price
        retribution.save()

        return retribution


class RetributionFilterForm(forms.Form):
    type = forms.MultipleChoiceField(choices=Retribution.TYPE, required=False,
                                     widget=forms.CheckboxSelectMultiple())
    transport = forms.MultipleChoiceField(
        choices=Retribution.TRANSPORT, required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.all(), widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def get_bookings(self):
        type = self.cleaned_data['type']
        transport = self.cleaned_data['transport']
        retributions = Retribution.objects.filter(destination__in=self.cleaned_data['destinations'])\
            .select_related('destination').order_by('-created')

        if type:
            retributions = retributions.filter(type__in=type)
        if transport:
            retributions = retributions.filter(transport__in=transport)

        return retributions
