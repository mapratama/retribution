from django import forms

from rumahtotok.apps.promotions.models import Promotion
from rumahtotok.apps.services.models import Service


class BasePromotionForm(forms.ModelForm):
    start_date = forms.DateField(input_formats=["%Y-%m-%d"])
    end_date = forms.DateField(input_formats=["%Y-%m-%d"])
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.select_related("treatment").order_by('-treatment_id'))

    class Meta:
        model = Promotion
        fields = '__all__'
