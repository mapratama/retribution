from django import forms

from retribution.apps.destinations.models import Destination
from retribution.apps.retributions.models import Retribution


class BaseRetributionForm(forms.ModelForm):

    destination = forms.ModelChoiceField(queryset=Destination.objects.all(),
                                         initial=Destination.objects.first())

    class Meta:
        model = Retribution
        fields = ('destination', 'type', 'quantity', 'transport',
                  'transport_id', 'mobile_number', 'email')

    def save(self, user, *args, **kwargs):
        kwargs['commit'] = False
        retribution = super(BaseRetributionForm, self).save(*args, **kwargs)
        retribution.created_by = user

        destination = self.cleaned_data['destination']
        price = retribution.quantity * destination.people_cost
        if retribution.transport == Retribution.TRANSPORT.motor:
            price = price + destination.motor_cost
        elif retribution.transport == Retribution.TRANSPORT.sedan:
            price = price + destination.sedan_cost
        elif retribution.transport == Retribution.TRANSPORT.mini_bus:
            price = price + destination.mini_bus_cost
        elif retribution.transport == Retribution.TRANSPORT.micro_bus:
            price = price + destination.micro_bus_cost
        elif retribution.transport == Retribution.TRANSPORT.bus:
            price = price + destination.bus_cost

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
    start_date = forms.DateField(input_formats=["%Y/%m/%d"], required=False)
    end_date = forms.DateField(input_formats=["%Y/%m/%d"], required=False)

    def clean(self):
        cleaned_data = super(RetributionFilterForm, self).clean()

        if self.errors:
            return cleaned_data

        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']

        if start_date > end_date:
            self.add_error("end_date", "Start date must be smaller than end date")

        return cleaned_data

    def get_bookings(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']
        type = self.cleaned_data['type']
        transport = self.cleaned_data['transport']
        retributions = Retribution.objects.filter(destination__in=self.cleaned_data['destinations'])\
            .select_related('destination').order_by('-created')

        if type:
            retributions = retributions.filter(type__in=type)
        if transport:
            retributions = retributions.filter(transport__in=transport)

        if start_date and end_date:
            retributions = retributions.filter(created__gte=start_date, created__lte=end_date)

        return retributions
