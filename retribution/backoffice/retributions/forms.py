from django import forms
from django.db.models import Q

from model_utils import Choices

from retribution.apps.destinations.models import Destination
from retribution.apps.retributions.models import Retribution
from retribution.core.utils import prepare_datetime_range


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

    TRANSPORT = Choices(
        (1, 'motor', 'Motor'),
        (2, 'sedan', 'Sedan'),
        (3, 'mini_bus', 'Mini Bus'),
        (4, 'micro_bus', 'Micro Bus'),
        (5, 'bus', 'Bus'),
        (6, 'other', 'Tanpa Kendaraan'),
    )

    transport = forms.MultipleChoiceField(
        choices=TRANSPORT, required=False,
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
        retributions = Retribution.objects \
            .filter(destination__in=self.cleaned_data['destinations'],
                    type__in=type) \
            .select_related('destination').order_by('-created')

        if start_date and end_date:
            start_date, end_date = prepare_datetime_range(start_date, end_date)
            retributions = retributions.filter(created__range=(start_date, end_date))

        if str(self.TRANSPORT.other) in transport:
            retributions = retributions.filter(
                Q(transport__in=transport) |
                Q(transport__isnull=True)
            )
        else:
            retributions = retributions.filter(transport__in=transport).exclude(transport__isnull=True)

        return retributions
