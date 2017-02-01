from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.bookings.models import Booking
from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.users.decorators import user_employee_required
from rumahtotok.apps.users.utils import send_android_push_notification
from rumahtotok.core.utils import normalize_phone, Page

from .forms import (BookingCreationForm, BookingFilterForm, BookingEditForm)


@user_employee_required
def index(request):
    employee = request.user.employees.first()
    store_ids = employee.stores.all().values_list("id", flat=True)
    initial = {
        'status': ['99'],
        'review_status': [BookingFilterForm.REVIEW_STATUS.reviewed,
                          BookingFilterForm.REVIEW_STATUS.not_reviewed],
        'store': store_ids
    }

    query_parameters = request.GET.copy()
    if 'page' in query_parameters:
        del query_parameters['page']

    form = BookingFilterForm(data=query_parameters or None, initial=initial, store_ids=store_ids)
    if form.is_valid():
        bookings = form.get_bookings()
        bookings = bookings.order_by('-date')
    else:
        bookings = Booking.objects.filter(store_id__in=store_ids)\
            .filter(status__in=[Booking.STATUS.new, Booking.STATUS.assigned])\
            .select_related("therapist__user")\
            .select_related("order__user").order_by('-date')

    query = request.GET.get('query', '').strip()
    if query:
        if query.isdigit():
            bookings = bookings.filter(
                user__mobile_number__startswith=normalize_phone(query)).order_by('-date')
        else:
            bookings = bookings.filter(
                Q(code__iexact=query) |
                Q(therapist__user__name__istartswith=query) |
                Q(order__user__name__istartswith=query)
            ).order_by('-date')

    if len(query_parameters) > 0:
        query_parameters = "&%s" % query_parameters.urlencode()
    else:
        query_parameters = ''

    page = request.GET.get('page', 1)
    paginator = Page(bookings, page, step=5)

    context_data = {
        'form': form,
        'bookings': paginator.objects,
        'query_parameters': query_parameters,
        'paginator': paginator,
        'title': 'Bookings',
    }

    if request.is_ajax():
        response = render_to_string(
            'backoffice/bookings/table_ajax.html',
            context_data, context_instance=RequestContext(request))
        return HttpResponse(response)

    return render(request, 'backoffice/bookings/index.html', context_data)


@user_employee_required
def add(request, order_id):
    order = get_object_or_404(Order, ~Q(status=Order.STATUS.created),
                              ~Q(status=Order.STATUS.completed), id=order_id)
    form = BookingCreationForm(data=request.POST or None, order=order,
                               created_by=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Booking has been successfully added')
        return redirect(reverse('backoffice:orders:detail', args=[order_id]))

    context_data = {
        'form': form,
        'order': order,
        'title': 'Add Booking',
    }
    return render(request, 'backoffice/bookings/add.html', context_data)


@user_employee_required
def edit(request, id):
    booking = get_object_or_404(Booking, id=id)
    form = BookingEditForm(data=request.POST or None, instance=booking, 
                           order=booking.order, created_by=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Booking has been successfully updated')
        return redirect('backoffice:bookings:index')

    context_data = {
        'form': form,
        'title': 'Edit Customer',
    }
    return render(request, 'backoffice/bookings/add.html', context_data)


@user_employee_required
def detail(request, id):
    booking = get_object_or_404(Booking, id=id)
    context_data = {
        'booking': booking,
        'title': 'Booking Detail',
    }
    return render(request, 'backoffice/bookings/details.html', context_data)


@user_employee_required
def cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if not booking.can_reprocessed():
        messages.errors(request, "Booking can't canceled")
    else:
        booking.cancel()
        messages.success(request, 'Booking has been successfully canceled')

    return redirect('backoffice:bookings:index')


@user_employee_required
def set_completed(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if not booking.can_reprocessed():
        messages.errors(request, "Booking can't set completed")
        return redirect('backoffice:bookings:index')

    booking.set_completed()
    messages.success(request, 'Booking has been successfully updated')
    send_android_push_notification(
        booking.order.user, "Booking Complete",
        "%s has been completed" % booking.code, booking.order.id)
    return redirect(reverse('backoffice:orders:detail', args=[booking.order_id]))
