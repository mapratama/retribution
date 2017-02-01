from django import forms
from django.contrib import auth
from django.utils import timezone
from datetime import datetime

from rumahtotok.core.utils import normalize_phone
from rumahtotok.core.validators import (validate_email_address,
                                        validate_mobile_number)
from rumahtotok.apps.users.models import User, Confirmation


class RegisterForm(forms.Form):
    email = forms.CharField(validators=[validate_email_address])
    mobile_number = forms.CharField(validators=[validate_mobile_number])
    name = forms.CharField(max_length=30)
    birthday = forms.CharField()
    gender = forms.ChoiceField(choices=User.GENDER)
    password = forms.CharField()
    gcm_key = forms.CharField(max_length=254, required=False)

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        try:
            birthday = datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            raise forms.ValidationError("%s is not a valid date. Please use YYYY-MM-DD format." % birthday)

        return birthday

    def clean_mobile_number(self):
        mobile_number = normalize_phone(self.cleaned_data['mobile_number'])
        user = User.objects.filter(mobile_number=mobile_number).first()
        if user:
            if user.created_from == User.CREATED_FROM.api:
                raise forms.ValidationError("This mobile number already in use")

        return mobile_number

    def clean_name(self):
        return self.cleaned_data['name'].title()

    def save(self, *args, **kwargs):
        mobile_number = self.cleaned_data['mobile_number']

        user, created = User.objects.update_or_create(
            username=mobile_number,
            defaults={
                'name': self.cleaned_data['name'],
                'email': self.cleaned_data['email'],
                'mobile_number': self.cleaned_data['mobile_number'],
                'gender': self.cleaned_data['gender'],
                'birthday': self.cleaned_data['birthday'],
                'gcm_key': self.cleaned_data['gcm_key'],
                'is_active': True,
                'type': User.TYPE.customer,
                'created_from': User.CREATED_FROM.api
            }
        )

        user.set_password(self.cleaned_data['password'])
        user.save()
        user.get_code()

        return user


class LoginForm(auth.forms.AuthenticationForm):
    username = forms.CharField(validators=[validate_mobile_number])
    gcm_key = forms.CharField(required=False)

    def clean_username(self):
        return normalize_phone(self.cleaned_data['username'])

    def save(self):
        user = self.get_user()
        gcm_key = self.cleaned_data["gcm_key"]

        if gcm_key:
            user.gcm_key = gcm_key
            user.save()

        return user


class GetConfirmationCodeForm(forms.Form):
    mobile_number = forms.CharField(validators=[validate_mobile_number])

    def clean_mobile_number(self):
        mobile_number = normalize_phone(self.cleaned_data['mobile_number'])

        if not User.objects.filter(mobile_number=mobile_number).exists():
            raise forms.ValidationError("Mobile number is not registered in Rumah Totok")

        return mobile_number

    def send_confirmation_code(self, async=True):
        mobile_number = self.cleaned_data['mobile_number']
        confirmation = Confirmation.new(mobile_number)

        # message = ("%s is confirmation code, for reset Rumah Totok app password") % \
        #     (confirmation.code, confirmation.valid_until.strftime("%d %b, %H:%M"))

        # send_sms(mobile, message, async)


class ResetPasswordForm(forms.Form):
    mobile_number = forms.CharField(validators=[validate_mobile_number])
    password = forms.CharField()
    code = forms.CharField(max_length=5)

    def clean_mobile_number(self):
        mobile_number = normalize_phone(self.cleaned_data['mobile_number'])

        if not User.objects.filter(mobile_number=mobile_number).exists():
            raise forms.ValidationError("Mobile number is not registered in Rumah Totok")

        return mobile_number

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()

        if self.errors:
            return cleaned_data

        code = self.cleaned_data['code']
        mobile_number = self.cleaned_data['mobile_number']

        if not Confirmation.objects.filter(
                mobile_number=mobile_number, code=code, is_active=True,
                valid_until__gte=timezone.now()).exists():
            self.add_error('code', '%s is not a valid code' % code)

        return cleaned_data

    def save(self, async=True):
        Confirmation.objects.filter(mobile_number=self.cleaned_data['mobile_number']).delete()

        user = User.objects.get(mobile_number=self.cleaned_data['mobile_number'])
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
