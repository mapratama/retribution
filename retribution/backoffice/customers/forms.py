from django import forms

from retribution.apps.users.models import User
from retribution.core.utils import normalize_phone
from retribution.core.validators import validate_email_address, validate_mobile_number


class BaseCustomerForm(forms.ModelForm):
    name = forms.CharField()
    username = forms.CharField()
    mobile_number = forms.CharField(validators=[validate_mobile_number])
    email = forms.CharField(required=False, validators=[validate_email_address])

    class Meta:
        model = User
        fields = ('username', 'name', 'mobile_number', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            return None
        return email

    def clean_mobile_number(self):
        return normalize_phone(self.cleaned_data['mobile_number'])


class CustomerEditForm(BaseCustomerForm):
    is_active = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CustomerEditForm, self).__init__(*args, **kwargs)
        user = kwargs['instance']
        self.fields['is_active'].initial = user.is_active

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        user = super(CustomerEditForm, self).save(*args, **kwargs)
        user.is_active = self.cleaned_data['is_active'] or None
        user.save()

        return user
