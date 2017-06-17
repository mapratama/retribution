from django import forms

from retribution.apps.destinations.models import Destination
from retribution.apps.users.models import User, Employee


class AddEmployeeForm(forms.Form):

    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True))
    destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def save(self):
        user = self.cleaned_data['user']
        employee = Employee.objects.create(user=user)
        employee.destinations.add(*self.cleaned_data['destinations'])
        return employee


class ChangeDestinationForm(forms.Form):
    destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def save(self, employee):
        employee.destinations.remove(*employee.destinations.all())
        employee.destinations.add(*self.cleaned_data['destinations'])
        return employee
