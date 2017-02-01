from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.users.decorators import user_employee_required
from rumahtotok.apps.balance_updates.models import BalanceUpdate
from rumahtotok.apps.users.models import User
from .forms import AddBalanceForm


@user_employee_required
def add(request, customer_id):
    user = get_object_or_404(User, id=customer_id)
    form = AddBalanceForm(data=request.POST or None)

    if form.is_valid():
        balance = form.save(user=user, created_by=request.user)
        messages.success(request, 'Customer balance successfully updated')
        return redirect(reverse('backoffice:customers:detail',
                        args=[balance.user.id]))

    context_data = {
        'form': form,
        'title': 'Add Balance',
    }
    return render(request, 'backoffice/add.html', context_data)


def details(request, id):
    balance = get_object_or_404(BalanceUpdate, id=id)

    context_data = {
        'balance': balance,
        'title': "Customer's Balance",
    }
    return render(request, 'backoffice/balances/details.html', context_data)
