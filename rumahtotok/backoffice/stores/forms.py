from django import forms

from rumahtotok.apps.stores.models import Store


class BaseStoreForm(forms.ModelForm):

    class Meta:
        model = Store
        fields = ('name', 'address', 'phone', 'BBM_pin', 'photo',
                  'max_male_booking', 'max_female_booking', 'lat', 'long', 'is_active')
