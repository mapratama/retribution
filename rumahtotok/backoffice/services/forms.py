from django import forms

from rumahtotok.apps.services.models import Service


class ServiceCreationForm(forms.ModelForm):

    class Meta:
        model = Service
        fields = ('name', 'time_needed', 'price', 'description',
                  'number_of_visit', 'number_of_people', 'is_active')

    def save(self, treatment, *args, **kwargs):
        kwargs['commit'] = False
        service = super(ServiceCreationForm, self).save(*args, **kwargs)
        service.treatment = treatment
        service.save()
        return service
