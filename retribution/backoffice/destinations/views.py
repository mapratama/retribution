from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from retribution.apps.destinations.models import Destination
from retribution.apps.users.decorators import user_employee_required
from retribution.core.utils import normalize_phone

from .forms import BaseDestinationForm


@user_employee_required
def index(request):
    destinations = Destination.objects.all()
    query = request.GET.get('query', '').strip()
    if query:
        destinations = destinations.filter(name__istartswith=query)

    context_data = {
        'destinations': destinations,
        'title': 'Customers',
    }
    return render(request, 'backoffice/destinations/index.html', context_data)


@user_employee_required
def add(request):
    form = BaseDestinationForm(data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Destination has been successfully added')
        return redirect(reverse('backoffice:destinations:index'))

    context_data = {
        'form': form,
        'title': 'Add Destination',
    }
    return render(request, 'backoffice/destinations/add.html', context_data)


@user_employee_required
def edit(request, id):
    destination = get_object_or_404(Destination, id=id)
    form = BaseDestinationForm(data=request.POST or None, instance=destination)
    if form.is_valid():
        form.save()
        messages.success(request, 'Destination has been successfully updated')
        return redirect('backoffice:destinations:index')

    context_data = {
        'form': form,
        'title': 'Edit Destination',
    }
    return render(request, 'backoffice/destinations/add.html', context_data)


@user_employee_required
def detail(request, id):
    destination = Destination.objects.get(id=id)
    context_data = {
        'destination': destination,
        'title': 'Destination details',
    }
    return render(request, 'backoffice/destinations/details.html', context_data)
