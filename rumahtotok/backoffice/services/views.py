from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.services.models import Service
from rumahtotok.apps.treatments.models import Treatment
from rumahtotok.apps.users.decorators import user_employee_required

from .forms import ServiceCreationForm


@user_employee_required
def add(request, treatment_id):
    treatment = get_object_or_404(Treatment, id=treatment_id)
    form = ServiceCreationForm(data=request.POST or None,
                           files=request.FILES or None)
    if form.is_valid():
        form.save(treatment=treatment)
        messages.success(request, 'Service has been successfully added')
        return redirect(reverse('backoffice:treatments:detail', args=[treatment_id]))

    context_data = {
        'form': form,
        'title': 'Add Service',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def edit(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    form = ServiceCreationForm(data=request.POST or None,
                               files=request.FILES or None,
                               instance=service)
    if form.is_valid():
        form.save(treatment=service.treatment)
        messages.success(request, 'Service has been successfully updated')
        return redirect(reverse('backoffice:treatments:detail', args=[service.treatment_id]))

    context_data = {
        'form': form,
        'title': 'Edit service',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def detail(request, service_id):
    service = Service.objects.get(id=service_id)
    context_data = {
        'service': service,
        'title': 'Service Detail',
    }
    return render(request, 'backoffice/services/details.html', context_data)
