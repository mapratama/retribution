from django.shortcuts import render

from rumahtotok.apps.users.decorators import user_employee_required

from rumahtotok.apps.bookings.utils import generate_booking_report
from rumahtotok.apps.orders.utils import generate_order_report
from rumahtotok.apps.payments.utils import generate_payment_report
from rumahtotok.core.utils import generate_zip_report

from .forms import BookingReportForm, OrderReportForm, BaseReportForm


@user_employee_required
def index(request):
    context_data = {
        'title': 'Reports',
        'username': request.user.name.title or request.user.username
    }
    return render(request, 'backoffice/reports/index.html', context_data)


@user_employee_required
def orders(request):
    form = OrderReportForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            statuses = form.cleaned_data['status']
            payment_statuses = form.cleaned_data['payment_statuses']
            start_date = form.cleaned_data['start']
            end_date = form.cleaned_data['end']

            report = generate_order_report(start_date, end_date, statuses=statuses,
                                           payment_statuses=payment_statuses)

            file_name = 'Order-report-{start_date}-{end_date}'.format(
                start_date=start_date,
                end_date=end_date)
            return generate_zip_report(report, file_name)

    context_data = {
        'form': form,
        'title': "Order Reports",
        'current_page': 'reports',
    }
    return render(request, 'backoffice/reports/form.html', context_data)


@user_employee_required
def bookings(request):
    form = BookingReportForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            therapist = form.cleaned_data['therapist']
            store = form.cleaned_data['store']
            start_date = form.cleaned_data['start']
            end_date = form.cleaned_data['end']

            report = generate_booking_report(start_date, end_date, therapist=therapist, store=store)

            file_name = '{store}-booking-report-{start_date}-{end_date}'.format(
                store=store.name if store else 'all-stores',
                start_date=start_date,
                end_date=end_date)
            return generate_zip_report(report, file_name)

    context_data = {
        'form': form,
        'title': "Booking Reports",
        'current_page': 'reports',
    }
    return render(request, 'backoffice/reports/form.html', context_data)


@user_employee_required
def payments(request):
    form = BaseReportForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            start_date = form.cleaned_data['start']
            end_date = form.cleaned_data['end']

            report = generate_payment_report(start_date, end_date)
            file_name = 'Payment-report-{start_date}-{end_date}'.format(
                start_date=start_date,
                end_date=end_date)
            return generate_zip_report(report, file_name)

    context_data = {
        'form': form,
        'title': "Payment Reports",
        'current_page': 'reports',
    }
    return render(request, 'backoffice/reports/form.html', context_data)
