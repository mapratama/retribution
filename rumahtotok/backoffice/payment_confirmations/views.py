from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from rumahtotok.apps.orders.models import PaymentConfirmation
from rumahtotok.apps.users.decorators import user_employee_required
from rumahtotok.apps.users.utils import send_android_push_notification
from rumahtotok.core.utils import Page

from .forms import PaymentConfirmationFilterForm, VerifiedPaymentForm


@user_employee_required
def index(request):
    initial = {
        'status': [PaymentConfirmation.STATUS.new,
                   PaymentConfirmation.STATUS.accepted,
                   PaymentConfirmation.STATUS.rejected]
    }

    query_parameters = request.GET.copy()
    if 'page' in query_parameters:
        del query_parameters['page']

    form = PaymentConfirmationFilterForm(data=query_parameters or None, initial=initial)
    if form.is_valid():
        confirmations = form.get_confirmations()
    else:
        confirmations = PaymentConfirmation.objects.select_related('order')\
            .select_related('correction_by').order_by('-created')

    query = request.GET.get('query', '').strip()
    if query:
        confirmations = confirmations.filter(
            Q(order__code__istartswith=query) |
            Q(order__user__name__istartswith=query)
        )

    if len(query_parameters) > 0:
        query_parameters = "&%s" % query_parameters.urlencode()
    else:
        query_parameters = ''

    page = request.GET.get('page', 1)
    paginator = Page(confirmations, page, step=5)

    context_data = {
        'form': form,
        'confirmations': paginator.objects,
        'paginator': paginator,
        'title': 'Order Confirmations',
        'query_parameters': query_parameters,
        'alert_sound': PaymentConfirmation.objects.filter(status=PaymentConfirmation.STATUS.new).exists(),
    }
    return render(request, 'backoffice/payment_confirmations/index.html', context_data)


@user_employee_required
def verified(request, id):
    confirmation = get_object_or_404(PaymentConfirmation, id=id)
    form = VerifiedPaymentForm(data=request.POST or None,
                               confirmation=confirmation,
                               instance=confirmation)
    if form.is_valid():
        confirmation = form.save(request.user)

        print confirmation.order.id

        if confirmation.status == PaymentConfirmation.STATUS.accepted:
            send_android_push_notification(
                confirmation.order.user, "Payment Confirmation",
                "Your payment has been verified", confirmation.order.id)
        else:
            send_android_push_notification(
                confirmation.order.user, "Payment Confirmation",
                "Sory, your payment rejected", confirmation.order.id)

        messages.success(request, 'Payment has been verified')
        return redirect('backoffice:payment_confirmations:index')

    context_data = {
        'form': form,
        'photo': confirmation.photo.url,
        'title': 'Verification',
    }
    return render(request, 'backoffice/payment_confirmations/edit.html', context_data)
