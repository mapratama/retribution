from django import forms

from model_utils import Choices

from retribution.apps.retributions.models import Retribution


class BaseRetributionForm(forms.ModelForm):

    class Meta:
        model = Retribution
        fields = ('destination', 'type', 'quantity', 'transport', 'transport_id', 'mobile_number')

    def save(self, user, *args, **kwargs):
        kwargs['commit'] = False
        retribution = super(BaseRetributionForm, self).save(*args, **kwargs)
        retribution.created_by = user

        price = retribution.quantity * 5000
        if retribution.transport == Retribution.TRANSPORT.motorcycle:
            price = price + 5000
        elif retribution.transport == Retribution.TRANSPORT.car:
            price = price + 15000

        retribution.price = price
        retribution.save()

        return retribution


class RetributionFilterForm(forms.Form):
    type = forms.MultipleChoiceField(choices=Retribution.TYPE, required=False,
                                     widget=forms.CheckboxSelectMultiple())
    transport = forms.MultipleChoiceField(choices=Retribution.TRANSPORT, required=False,
                                          widget=forms.CheckboxSelectMultiple())

    def get_bookings(self):
        type = self.cleaned_data['type']
        transport = self.cleaned_data['transport']
        retributions = Retribution.objects.select_related('destination').order_by('-created')

        if type:
            retributions = retributions.filter(type__in=type)
        if transport:
            retributions = retributions.filter(transport__in=transport)

        return retributions
