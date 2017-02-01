from rumahtotok.apps.payments.models import Payment
from rumahtotok.core.utils import prepare_datetime_range


def generate_payment_report(start_date, end_date):
    rows = []
    rows.append(['Start:', start_date.strftime('%Y/%m/%d'),
                 'End:', end_date.strftime('%Y/%m/%d')])
    rows.append('')
    header = (
        'Code',
        'Order Code',
        'Customer Name',
        'Date',
        'Time',
        'Value',
        'Created by',
        'Notes',
    )

    rows.append(header)
    start_date, end_date = prepare_datetime_range(start_date, end_date)
    payments = Payment.objects.prefetch_related("order", "order__user")\
        .select_related('created_by').filter(time__range=(start_date, end_date))\
        .order_by('time')

    for payment in payments:
        row_content = [payment.code,
                       payment.order.code,
                       payment.order.user.name,
                       payment.time.strftime('%Y/%m/%d'),
                       payment.time.strftime('%H:%M'),
                       "{:,}".format(payment.value),
                       payment.created_by,
                       payment.notes]
        rows.append(row_content)

    return rows
