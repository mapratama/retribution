from django import forms

from rumahtotok.apps.users.models import User
from rumahtotok.core.utils import normalize_phone
from rumahtotok.core.validators import validate_email_address, validate_mobile_number


class BaseCustomerForm(forms.ModelForm):
    name = forms.CharField()
    mobile_number = forms.CharField(validators=[validate_mobile_number])
    gender = forms.ChoiceField(choices=User.GENDER)
    address = forms.CharField(required=False, widget=forms.Textarea)
    email = forms.CharField(required=False, validators=[validate_email_address])

    class Meta:
        model = User
        fields = ('name', 'mobile_number', 'gender', 'birthday', 'email', 'address')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            return None
        return email

    def clean_mobile_number(self):
        return normalize_phone(self.cleaned_data['mobile_number'])


class CustomerCreationForm(BaseCustomerForm):
    def __init__(self, *args, **kwargs):
        super(CustomerCreationForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        user = super(CustomerCreationForm, self).save(*args, **kwargs)
        user.type = user.TYPE.customer
        user.mobile_number = self.cleaned_data['mobile_number']
        user.username = self.cleaned_data['mobile_number']
        user.created_from = User.CREATED_FROM.backoffice
        user.save()

        user.get_code()

        return user


class CustomerEditForm(BaseCustomerForm):
    is_active = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CustomerEditForm, self).__init__(*args, **kwargs)
        user = kwargs['instance']
        self.fields['email'].initial = user.email
        self.fields['is_active'].initial = user.is_active
        self.fields['gender'].initial = user.gender
        self.fields['birthday'].initial = user.birthday

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        user = super(CustomerEditForm, self).save(*args, **kwargs)
        user.email = self.cleaned_data['email'] or None
        user.is_active = self.cleaned_data['is_active'] or None
        user.birthday = self.cleaned_data['birthday'] or None
        user.gender = self.cleaned_data['gender'] or None

        user.save()
        user.get_code()

        return user
