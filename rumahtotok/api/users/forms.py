from django import forms
from datetime import datetime

from rumahtotok.core.validators import validate_email_address
from rumahtotok.apps.users.models import User


class UpdateProfileForm(forms.Form):
    email = forms.CharField(validators=[validate_email_address])
    name = forms.CharField(max_length=30)
    birthday = forms.CharField()
    gender = forms.ChoiceField(choices=User.GENDER)

    def clean_birthday(self):
        birthday = self.cleaned_data.get('birthday')

        try:
            birthday = datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            raise forms.ValidationError("%s is not a valid date. Please use YYYY-MM-DD format." % birthday)

        return birthday

    def save(self, user, *args, **kwargs):
        data = self.cleaned_data
        user.name = data['name']
        user.email = data['email']
        user.birthday = data['birthday']
        user.gender = data['gender']
        user.save()

        return user
