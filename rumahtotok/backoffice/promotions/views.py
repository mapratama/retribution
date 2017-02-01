from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.promotions.models import Promotion
from rumahtotok.apps.users.decorators import user_employee_required
from .forms import BasePromotionForm


@user_employee_required
def index(request):
    promotions = Promotion.objects.order_by('-id')
    context_data = {
        'promotions': promotions,
        'title': 'Promotions',
    }
    return render(request, 'backoffice/promotions/index.html', context_data)


@user_employee_required
def add(request):
    form = BasePromotionForm(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Promotion has been successfully added')
        return redirect(reverse('backoffice:promotions:index'))

    context_data = {
        'form': form,
        'title': 'Add Promotion',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def edit(request, id):
    treatment = get_object_or_404(Promotion, id=id)
    form = BasePromotionForm(data=request.POST or None,
                             files=request.FILES or None,
                             instance=treatment)
    if form.is_valid():
        form.save()
        messages.success(request, 'Promotion has been successfully updated')
        return redirect('backoffice:promotions:index')

    context_data = {
        'form': form,
        'title': 'Edit Promotion',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def detail(request, id):
    promotion = get_object_or_404(Promotion, id=id)
    context_data = {
        'promotion': promotion,
        'title': 'Promotion Detail',
    }
    return render(request, 'backoffice/promotions/details.html', context_data)
