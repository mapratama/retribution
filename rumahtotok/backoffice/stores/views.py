from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from rumahtotok.apps.stores.models import Store
from rumahtotok.apps.users.decorators import user_employee_required

from .forms import BaseStoreForm


@user_employee_required
def index(request):
    stores = Store.objects.all()
    context_data = {
        'stores': stores,
        'title': 'Stores',
    }
    return render(request, 'backoffice/stores/index.html', context_data)


@user_employee_required
def add(request):
    form = BaseStoreForm(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Store has been successfully added')
        return redirect(reverse('backoffice:stores:index'))

    context_data = {
        'form': form,
        'title': 'Add Stores',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def edit(request, id):
    treatment = get_object_or_404(Store, id=id)
    form = BaseStoreForm(data=request.POST or None,
                         files=request.FILES or None,
                         instance=treatment)
    if form.is_valid():
        form.save()
        messages.success(request, 'Store has been successfully updated')
        return redirect('backoffice:stores:index')

    context_data = {
        'form': form,
        'title': 'Edit Store',
    }
    return render(request, 'backoffice/add.html', context_data)


def detail(request, id):
    store = Store.objects.get(id=id)
    context_data = {
        'store': store,
        'therapists': store.therapists.all().select_related("user"),
        'title': 'Store Detail',
    }
    return render(request, 'backoffice/stores/details.html', context_data)


@user_employee_required
def get_therapist(request):
    store = Store.objects.get(id=request.GET.get('store'))
    if not store:
        return HttpResponseBadRequest()
    context = {'therapists': list(store.therapists.all())}
    data = render_to_string(
        'backoffice/stores/therapists_ajax.html',
        context, context_instance=RequestContext(request))

    return HttpResponse(data)
