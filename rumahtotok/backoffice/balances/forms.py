from django import forms
from django.core.validators import MinValueValidator
from model_utils import Choices

from rumahtotok.apps.balance_updates.models import BalanceUpdate
from rumahtotok.apps.balance_updates.utils import create_balance_update


class AddBalanceForm(forms.Form):
    TYPES = Choices(
        (1, 'add', 'Add'),
        (2, 'deduct', 'Deduct')
    )
    type = forms.ChoiceField(choices=TYPES, initial=TYPES.add)
    value = forms.FloatField(validators=[MinValueValidator(1)])
    notes = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data = super(AddBalanceForm, self).clean()

        if self.errors:
            return cleaned_data

        if int(self.cleaned_data['type']) == self.TYPES.deduct:
            cleaned_data['value'] = -cleaned_data['value']

        return cleaned_data

    def save(self, user, created_by, *args, **kwargs):
        balance_update = create_balance_update(
            user=user, value=self.cleaned_data['value'], type=BalanceUpdate.TYPES.manual,
            created_by=created_by, notes=self.cleaned_data['notes'])

        return balance_update
