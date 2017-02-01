from django import forms
from model_utils import Choices

from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.stores.models import Store
from rumahtotok.apps.therapists.models import Therapist


class BaseReportForm(forms.Form):
    start = forms.DateField(input_formats=["%Y/%m/%d"], label="Start Date")
    end = forms.DateField(input_formats=["%Y/%m/%d"], label="End Date")

    def clean(self):
        cleaned_data = super(BaseReportForm, self).clean()

        if self.errors:
            return cleaned_data

        if cleaned_data['start'] > cleaned_data['end']:
            self.add_error('start', "Start time can't be greater than end time")


class BookingReportForm(BaseReportForm):
    therapist = forms.ModelChoiceField(queryset=Therapist.objects.select_related("user"), required=False,
                                       empty_label="--- All Partners ---")

    store = forms.ModelChoiceField(queryset=Store.objects.all(), required=False,
                                   empty_label="--- All Partners ---")


class OrderReportForm(BaseReportForm):
    status = forms.MultipleChoiceField(choices=Order.STATUS, required=False,
                                       widget=forms.CheckboxSelectMultiple())
    PAYMENT_STATUS = Choices(
        ('1', 'paid', 'Paid'),
        ('2', 'credit', 'Credit'),
    )
    payment_statuses = forms.MultipleChoiceField(choices=PAYMENT_STATUS, required=False,
                                                 widget=forms.CheckboxSelectMultiple())
