from django import forms
from model_utils import Choices

from rumahtotok.apps.orders.models import PaymentConfirmation
from rumahtotok.apps.payments.models import Payment


class VerifiedPaymentForm(forms.ModelForm):
    STATUS = Choices(
        (2, 'accepted', 'Accepted'),
        (3, 'rejected', 'Rejected')
    )
    status = forms.TypedChoiceField(choices=STATUS, coerce=int,
                                    initial=STATUS.accepted)
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = PaymentConfirmation
        fields = ('value', 'status', 'notes')

    def __init__(self, confirmation, *args, **kwargs):
        super(VerifiedPaymentForm, self).__init__(*args, **kwargs)
        self.confirmation = confirmation

    def clean(self):
        cleaned_data = super(VerifiedPaymentForm, self).clean()

        if self.errors:
            return cleaned_data

        value = cleaned_data['value']
        status = cleaned_data['status']
        notes = cleaned_data['notes']

        if status == self.STATUS.rejected:
            if not notes:
                self.add_error('notes', 'For rejected payment, notes must be filled')

        if status == self.STATUS.accepted:
            if self.confirmation.order.completed_paid:
                raise forms.ValidationError('Please rejected payment, This order has been completed paid')

            if self.confirmation.order.payments.count() > 0:
                raise forms.ValidationError('Please rejected payment, This order has been verified payment')

            if not value:
                self.add_error('value', 'For accepted payment, value must be filled')
            elif self.confirmation.order.unique_price != value:
                self.add_error('value', 'Not order with unique price %s' % value)

        return cleaned_data

    def save(self, user, *args, **kwargs):
        confirmation = super(VerifiedPaymentForm, self).save(*args, **kwargs)
        if confirmation.status == self.STATUS.accepted:
            order = confirmation.order
            order.payments.create(
                balance_used=0, value=order.discounted_price, method=Payment.METHOD.transfer,
                notes="Create from accepted payment confirmation")

            order.calculate_total_payment()
            order.update_payment_status()
            order.update_status()

        confirmation.correction_by = user
        confirmation.save()
        return confirmation


class PaymentConfirmationFilterForm(forms.Form):
    STATUS = Choices(
        (str(PaymentConfirmation.STATUS.new), 'new', 'New'),
        (str(PaymentConfirmation.STATUS.accepted), 'accepted', 'Accepted'),
        (str(PaymentConfirmation.STATUS.rejected), 'rejected', 'Rejected')
    )
    status = forms.MultipleChoiceField(choices=STATUS, required=False,
                                       widget=forms.CheckboxSelectMultiple())

    def get_confirmations(self):
        statuses = self.cleaned_data['status']
        confirmations = PaymentConfirmation.objects.select_related('order')\
            .select_related('correction_by').order_by('-created')

        if statuses:
            list_filter = []
            if self.STATUS.new in statuses:
                list_filter.append(self.STATUS.new)

            if self.STATUS.accepted in statuses:
                list_filter.append(self.STATUS.accepted)

            if self.STATUS.rejected in statuses:
                list_filter.append(self.STATUS.rejected)

            confirmations = confirmations.filter(status__in=list_filter)

        return confirmations
