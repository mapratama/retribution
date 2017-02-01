from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum, F
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.bookings.models import Booking
from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.users.decorators import user_employee_required
from rumahtotok.core.utils import Page, normalize_phone

from .forms import OrderCreationForm, OrderFilterForm


@user_employee_required
def index(request):
    initial = {
        'status': ['99'],
        'payment_status': [OrderFilterForm.PAYMENT_STATUS.paid,
                           OrderFilterForm.PAYMENT_STATUS.credit]
    }

    query_parameters = request.GET.copy()
    if 'page' in query_parameters:
        del query_parameters['page']

    form = OrderFilterForm(data=query_parameters or None, initial=initial)
    if form.is_valid():
        orders = form.get_orders()
    else:
        orders = Order.objects.exclude(status=Order.STATUS.canceled)\
            .exclude(status=Order.STATUS.completed)\
            .select_related('user').select_related('service').order_by('-id')

    query = request.GET.get('query', '').strip()
    if query:
        if query.isdigit():
            orders = orders.filter(
                user__mobile_number__startswith=normalize_phone(query))
        else:
            orders = orders.filter(
                Q(code__iexact=query) |
                Q(user__name__istartswith=query)
            )

    if len(query_parameters) > 0:
        query_parameters = "&%s" % query_parameters.urlencode()
    else:
        query_parameters = ''

    page = request.GET.get('page', 1)
    paginator = Page(orders, page, step=5)

    context_data = {
        'form': form,
        'orders': paginator.objects,
        'paginator': paginator,
        'title': 'Orders',
        'query_parameters': query_parameters,
    }
    return render(request, 'backoffice/orders/index.html', context_data)


@user_employee_required
def add(request):
    form = OrderCreationForm(data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Order has been successfully added')
        return redirect(reverse('backoffice:orders:index'))

    context_data = {
        'form': form,
        'title': 'Add Order',
    }
    return render(request, 'backoffice/orders/add.html', context_data)


@user_employee_required
def detail(request, id):
    order = Order.objects.filter(id=id).select_related('user')\
        .select_related('service').first()

    if not order:
        raise Http404("Order does not exist")

    payments = order.payments.order_by('time')

    context_data = {
        'order': order,
        'bookings': order.bookings.select_related('store').select_related('therapist__user').order_by('-date'),
        'payments': payments,
        'title': 'Detail Order',
    }
    return render(request, 'backoffice/orders/details.html', context_data)


@user_employee_required
def cancel(request, id):
    order = get_object_or_404(Order, id=id)

    if not order.can_canceled():
        messages.error(request, "This order can't be canceled")
        return redirect(reverse('backoffice:orders:detail', args=[order.id]))

    order.cancel(user=request.user)
    messages.success(request, "Order has been succesfully canceled")
    return redirect(reverse('backoffice:orders:detail', args=[order.id]))


@user_employee_required
def reverse_balance(request, id):
    order = get_object_or_404(Order, id=id)

    if not order.can_reverse_payment():
        messages.error(request, "This order balance can't be reversed.")
        return redirect(reverse('backoffice:orders:detail', args=[order.id]))

    order.reverse_payment(request.user)
    messages.success(request, "Balance has been succesfully reversed")
    return redirect(reverse('backoffice:customers:detail', args=[order.user.id]))


@user_employee_required
def invoice_print(request, id):
    employee = request.user.employees.last()
    store = employee.stores.last()

    order = Order.objects.filter(id=id).select_related('user')\
        .select_related('service').first()

    if not order:
        raise Http404("Order does not exist")

    payments = order.payments.annotate(total=Sum(F("value") + F("balance_used")))\
        .order_by('time')

    bookings = order.bookings.exclude(status=Booking.STATUS.canceled) \
        .select_related('store').select_related('therapist__user')

    context_data = {
        'store': order.bookings.last().store if order.bookings.exists() else store,
        'order': order,
        'bookings': bookings,
        'payments': payments,
        'title': 'Detail Order',
    }
    return render(request, 'backoffice/orders/print.html', context_data)
