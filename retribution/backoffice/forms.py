from django import forms

from retribution.core.utils import api_call


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'autocomplete': 'off'}))

    def save(self):
        BASE_URL = 'http://104.131.8.149/api'
        TOKEN = 'kajfhasb2374632r9qdg476dgko345hl1'

        url = BASE_URL + "/auth/login"
        payloads = {
            'token': TOKEN,
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password'],
        }
        return api_call('POST', url, payloads)
