from django import forms

from retribution.apps.users.models import User
from retribution.apps.destinations.models import Destination
from retribution.core.utils import normalize_phone
from retribution.core.validators import validate_email_address, validate_mobile_number


class BaseUserForm(forms.ModelForm):
    name = forms.CharField()
    username = forms.CharField()
    mobile_number = forms.CharField(validators=[validate_mobile_number])
    email = forms.CharField(required=False, validators=[validate_email_address])
    destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'name', 'mobile_number', 'email', 'destinations')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            return None
        return email

    def clean_mobile_number(self):
        return normalize_phone(self.cleaned_data['mobile_number'])

    def save(self, *args, **kwargs):
        user = super(BaseUserForm, self).save(*args, **kwargs)
        user.destinations.add(*self.cleaned_data['destinations'])
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True
        user.save()
        return user


class UserEditForm(BaseUserForm):
    is_active = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        user = kwargs['instance']
        self.fields['is_active'].initial = user.is_active

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        user = super(UserEditForm, self).save(*args, **kwargs)
        user.is_active = self.cleaned_data['is_active'] or None
        user.save()

        user.destinations.remove(*user.destinations.all())
        user.destinations.add(*self.cleaned_data['destinations'])

        return user
