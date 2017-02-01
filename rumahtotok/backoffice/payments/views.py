from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.payments.models import Payment
from rumahtotok.apps.users.decorators import user_employee_required

from .forms import PaymentCreationForm


@user_employee_required
def add(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    form = PaymentCreationForm(data=request.POST or None, order=order, created_by=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Payment has been successfully added')
        return redirect(reverse('backoffice:orders:detail', args=[order_id]))

    context_data = {
        'form': form,
        'title': 'Add Payment',
    }
    return render(request, 'backoffice/add.html', context_data)


@user_employee_required
def detail(request, payment_id):
    payment = Payment.objects.get(id=payment_id)

    context_data = {
        'payment': payment,
        'title': 'Payment Detail',
    }
    return render(request, 'backoffice/payments/details.html', context_data)
