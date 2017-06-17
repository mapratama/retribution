from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from retribution.apps.users.models import User
from retribution.apps.users.decorators import user_employee_required
from retribution.core.utils import normalize_phone

from .forms import CustomerEditForm, BaseCustomerForm


@user_employee_required
def index(request):
    users = User.objects.filter(is_active=True)
    query = request.GET.get('query', '').strip()
    if query:
        if query.isdigit():
            users = users.filter(
                mobile_number__startswith=normalize_phone(query))
        else:
            users = users.filter(
                Q(name__istartswith=query) |
                Q(email__istartswith=query)
            )

    context_data = {
        'users': users,
        'title': 'Customers',
    }
    return render(request, 'backoffice/customers/index.html', context_data)


@user_employee_required
def add(request):
    form = BaseCustomerForm(data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Customer has been successfully added')
        return redirect(reverse('backoffice:customers:index'))

    context_data = {
        'form': form,
        'title': 'Add Customer',
    }
    return render(request, 'backoffice/customers/add.html', context_data)


@user_employee_required
def edit(request, id):
    user = get_object_or_404(User, id=id)
    form = CustomerEditForm(data=request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Customer has been successfully updated')
        return redirect('backoffice:customers:index')

    context_data = {
        'form': form,
        'title': 'Edit Customer',
    }
    return render(request, 'backoffice/customers/add.html', context_data)


@user_employee_required
def detail(request, id):
    user = User.objects.get(id=id)
    context_data = {
        'user': user,
        'title': 'Customer details',
    }
    return render(request, 'backoffice/customers/details.html', context_data)