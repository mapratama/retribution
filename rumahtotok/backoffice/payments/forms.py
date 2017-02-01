from django import forms
from django.conf import settings

from rumahtotok.apps.payments.models import Payment
from rumahtotok.apps.orders.utils import get_balance_to_use


class PaymentCreationForm(forms.ModelForm):
    def __init__(self, order, created_by, *args, **kwargs):
        super(PaymentCreationForm, self).__init__(*args, **kwargs)
        self.created_by = created_by
        self.order = order
        self.balance_to_use = get_balance_to_use(self.order.discounted_price,
                                                 self.order.user)
        self.fields['balance_used'].initial = self.balance_to_use
        self.fields['value'].initial = 0

    class Meta:
        model = Payment
        fields = ('balance_used', 'value', 'notes')

    def clean_balance_used(self):
        balance_used = self.cleaned_data['balance_used']
        user_balance = self.order.user.balance
        if balance_used > user_balance:
            raise forms.ValidationError(
                "Customer's total balance is %s" % "{:,}".format(user_balance))

        return balance_used

    def clean(self):
        cleaned_data = super(PaymentCreationForm, self).clean()
        if self.errors:
            return cleaned_data

        balance_used = cleaned_data['balance_used']
        total_value = cleaned_data['value'] + balance_used
        minimum_value = settings.MINIMUM_PAYMENT * self.order.discounted_price

        if not self.order.total_payment and total_value < minimum_value:
            raise forms.ValidationError(
                "Your minimum payment is %s" % "{:,}".format(minimum_value))

        if total_value > self.order.remaining_payment:
            self.add_error(
                'value', 'Remining payment is %s' % "{:,}".format(self.order.remaining_payment))

        return cleaned_data

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        payment = super(PaymentCreationForm, self).save(*args, **kwargs)
        payment.order = self.order
        payment.balance_used = self.cleaned_data['balance_used']
        payment.created_by = self.created_by
        payment.save()

        payment.update_balance()

        self.order.calculate_total_payment()
        self.order.update_status()

        return payment
