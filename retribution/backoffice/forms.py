from django import forms
from django.conf import settings

from retribution.core.utils import api_call


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'autocomplete': 'off'}))

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        url = settings.BASE_URL + "/auth/login"
        payloads = {
            'token': settings.TOKEN,
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password'],
        }
        response = api_call('POST', url, payloads)

        if response['status_code'] > 400:
            self.add_error('username', "Maaf server sedang mengalami ganggguan")
        if response['status_code'] == 400:
            self.add_error('username', "Username dan password tidak sesuai")
        else:
            self.user_response = response

        return cleaned_data
