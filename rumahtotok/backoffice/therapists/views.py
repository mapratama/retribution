from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from rumahtotok.apps.therapists.models import Therapist
from rumahtotok.apps.users.decorators import user_employee_required, super_user_required

from .forms import TherapistCreationForm, TherapistEditForm


@user_employee_required
def index(request):
    therapists = Therapist.objects.select_related('user').select_related('store')\
        .order_by('-store')

    context_data = {
        'therapists': therapists,
        'title': 'Therapists',
    }
    return render(request, 'backoffice/therapists/index.html', context_data)


@user_employee_required
def add(request):
    form = TherapistCreationForm(data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Therapist has been successfully added')
        return redirect(reverse('backoffice:therapists:index'))

    context_data = {
        'form': form,
        'title': 'Add Therapist',
    }
    return render(request, 'backoffice/add.html', context_data)


@super_user_required
def edit(request, id):
    therapist = get_object_or_404(Therapist, id=id)
    form = TherapistEditForm(data=request.POST or None, therapist=therapist)
    if form.is_valid():
        form.save()
        messages.success(request, 'Therapist has been successfully updated')
        return redirect('backoffice:therapists:index')

    context_data = {
        'form': form,
        'title': 'Edit Therapist',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def detail(request, id):
    therapist = get_object_or_404(Therapist, id=id)

    context_data = {
        'therapist': therapist,
        'title': 'Therapist Detail',
    }
    return render(request, 'backoffice/therapists/details.html', context_data)
