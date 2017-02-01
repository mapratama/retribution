from django import forms

from rumahtotok.apps.treatments.models import Treatment


class BaseTreatmentForm(forms.ModelForm):

    class Meta:
        model = Treatment
        fields = ('name', 'icon', 'photo', 'description', 'is_active', 'position')
