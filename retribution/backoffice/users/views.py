from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from retribution.apps.users.models import User
from retribution.apps.users.decorators import user_employee_required
from retribution.core.utils import normalize_phone

from .forms import UserEditForm, UserCreationForm


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
        'title': 'Users',
    }
    return render(request, 'backoffice/users/index.html', context_data)


@user_employee_required
def add(request):
    form = UserCreationForm(data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'User has been successfully added')
        return redirect(reverse('backoffice:users:index'))

    context_data = {
        'form': form,
        'title': 'Add User',
    }
    return render(request, 'backoffice/users/add.html', context_data)


@user_employee_required
def edit(request, id):
    user = get_object_or_404(User, id=id)
    form = UserEditForm(data=request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, 'User has been successfully updated')
        return redirect('backoffice:users:index')

    context_data = {
        'form': form,
        'title': 'Edit User',
    }
    return render(request, 'backoffice/users/add.html', context_data)


@user_employee_required
def detail(request, id):
    user = User.objects.get(id=id)
    context_data = {
        'user_data': user,
        'destinations': user.destinations.all(),
        'title': 'User Details',
    }
    return render(request, 'backoffice/users/details.html', context_data)
