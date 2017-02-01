from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.treatments.models import Treatment
from rumahtotok.apps.users.decorators import user_employee_required

from .forms import BaseTreatmentForm


@user_employee_required
def index(request):
    treatments = Treatment.objects.order_by('position')
    context_data = {
        'treatments': treatments,
        'title': 'Treatments',
    }
    return render(request, 'backoffice/treatments/index.html', context_data)


@user_employee_required
def add(request):
    form = BaseTreatmentForm(data=request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        form.save()
        messages.success(request, 'Treatment has been successfully added')
        return redirect(reverse('backoffice:treatments:index'))

    context_data = {
        'form': form,
        'title': 'Add Treatment',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def edit(request, id):
    treatment = get_object_or_404(Treatment, id=id)
    form = BaseTreatmentForm(data=request.POST or None,
                             files=request.FILES or None,
                             instance=treatment)
    if form.is_valid():
        form.save()
        messages.success(request, 'Treatment has been successfully updated')
        return redirect('backoffice:treatments:index')

    context_data = {
        'form': form,
        'title': 'Edit Treatment',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def detail(request, id):
    treatment = get_object_or_404(Treatment, id=id)
    context_data = {
        'treatment': treatment,
        'services': treatment.services.all(),
        'title': 'Treatment Detail',
    }
    return render(request, 'backoffice/treatments/details.html', context_data)


@user_employee_required
def get_products(request):
    treatment = Treatment.objects.get(id=request.GET.get('treatment'))
    if not treatment:
        return HttpResponseBadRequest()
    context = {'services': list(treatment.services.all())}
    data = render_to_string(
        'backoffice/treatments/services_ajak.html',
        context, context_instance=RequestContext(request))

    return HttpResponse(data)
