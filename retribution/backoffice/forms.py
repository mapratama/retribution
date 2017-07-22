from django import forms
from django.conf import settings

from retribution.core.utils import api_call


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'autocomplete': 'off'}))

    def save(self):
        url = settings.BASE_URL + "/auth/login"
        payloads = {
            'token': settings.TOKEN,
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password'],
        }
        return api_call('POST', url, payloads)
