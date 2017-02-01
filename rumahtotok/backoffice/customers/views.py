import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.users.models import User
from rumahtotok.apps.users.decorators import user_employee_required
from rumahtotok.core.utils import normalize_phone
from rumahtotok.core.serializers import serialize_user

from .forms import CustomerCreationForm, CustomerEditForm


@user_employee_required
def index(request):
    users = User.objects.filter(type=User.TYPE.customer, is_active=True)
    query = request.GET.get('query', '').strip()
    if query:
        if query.isdigit():
            users = users.filter(
                mobile_number__startswith=normalize_phone(query))
        else:
            users = users.filter(
                Q(code__istartswith=query) |
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
    form = CustomerCreationForm(data=request.POST or None)
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
    balance_updates = user.balance_updates.all().order_by("-id")[0:50]
    context_data = {
        'balance_updates': balance_updates,
        'user': user,
        'title': 'Customer details',
    }
    return render(request, 'backoffice/customers/details.html', context_data)


@user_employee_required
def search(request):
    suggestions = []
    users = User.objects.filter(
        type=User.TYPE.customer,
        name__icontains=request.GET.get('query', ''))[:5]

    for user in users:
        user = {
            "name": user.name,
            "phone": user.mobile_number,
        }
        suggestions.append(user)
    return HttpResponse(json.dumps(suggestions), content_type="application/json")


@user_employee_required
def get_data(request):
    user = get_object_or_404(User, mobile_number=request.GET.get('mobile_number'))
    customer_data = serialize_user(user)
    return JsonResponse(customer_data)
