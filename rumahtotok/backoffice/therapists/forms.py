from django import forms

from rumahtotok.apps.stores.models import Store
from rumahtotok.apps.therapists.models import Therapist
from rumahtotok.apps.users.models import User

from rumahtotok.core.utils import normalize_phone
from rumahtotok.core.validators import validate_mobile_number


class BaseTherapistForm(forms.Form):
    name = forms.CharField()
    mobile_number = forms.CharField(validators=[validate_mobile_number])
    gender = forms.ChoiceField(choices=User.GENDER, initial=User.GENDER.female)
    max_booking = forms.IntegerField()
    address = forms.CharField(required=False, widget=forms.Textarea)
    store = forms.ModelChoiceField(label='Store', queryset=None)

    def __init__(self, *args, **kwargs):
        super(BaseTherapistForm, self).__init__(*args, **kwargs)
        self.fields['store'].queryset = Store.objects.all()

    def clean_mobile_number(self):
        mobile_number = normalize_phone(self.cleaned_data['mobile_number'])
        if User.objects.filter(mobile_number=mobile_number).exists():
            raise forms.ValidationError("User with this Mobile Number already exists.")

        return mobile_number


class TherapistCreationForm(BaseTherapistForm):
    def save(self, *args, **kwargs):
        user = User.objects.create(
            name=self.cleaned_data['name'],
            mobile_number=self.cleaned_data['mobile_number'],
            address=self.cleaned_data['address'],
            gender=self.cleaned_data['gender'],
            username=self.cleaned_data['mobile_number'],
            type=User.TYPE.therapist
        )
        user.get_code()
        therapist = Therapist.objects.create(
            user=user,
            store=self.cleaned_data['store'],
            max_booking=self.cleaned_data['max_booking'])

        return therapist


class TherapistEditForm(BaseTherapistForm):
    is_active = forms.BooleanField(required=False)

    def __init__(self, therapist, *args, **kwargs):
        super(TherapistEditForm, self).__init__(*args, **kwargs)
        self.therapist = therapist
        self.fields['name'].initial = self.therapist.user.name
        self.fields['mobile_number'].initial = self.therapist.user.mobile_number
        self.fields['address'].initial = self.therapist.user.address
        self.fields['store'].initial = self.therapist.store
        self.fields['gender'].initial = self.therapist.user.gender
        self.fields['max_booking'].initial = self.therapist.max_booking
        self.fields['is_active'].initial = self.therapist.is_active

    def clean_mobile_number(self):
        mobile_number = normalize_phone(self.cleaned_data['mobile_number'])
        if User.objects.filter(mobile_number=mobile_number).exclude(id=self.therapist.user_id).exists():
            raise forms.ValidationError("User with this Mobile Number already exists.")

        return mobile_number

    def save(self, *args, **kwargs):
        user = self.therapist.user
        user.name = self.cleaned_data['name']
        user.gender = self.cleaned_data['gender']
        user.mobile_number = self.cleaned_data['mobile_number']
        user.address = self.cleaned_data['address']
        user.username = self.cleaned_data['mobile_number']
        user.save()
        user.get_code()

        self.therapist.store = self.cleaned_data['store']
        self.therapist.is_active = self.cleaned_data['is_active']
        self.therapist.max_booking = self.cleaned_data['max_booking']
        self.therapist.save()

        return
