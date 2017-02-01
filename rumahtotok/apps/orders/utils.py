from rumahtotok.apps.bookings.models import Booking
from rumahtotok.apps.orders.models import Order
from rumahtotok.backoffice.reports.forms import OrderReportForm
from rumahtotok.core.utils import prepare_datetime_range


def generate_order_report(start_date, end_date, statuses=None, payment_statuses=None):
    rows = []
    rows.append(['Start:', start_date.strftime('%Y/%m/%d'),
                 'End:', end_date.strftime('%Y/%m/%d')])
    rows.append('')
    header = (
        'Code',
        'user',
        'Created',
        'Service',
        'Status',
        'Price',
        'Promotion ',
        'Discount',
        'Discounted Price',
        'Number of Visit',
        'Payment Status'
    )
    rows.append(header)
    start_date, end_date = prepare_datetime_range(start_date, end_date)
    orders = Order.objects.select_related('user').select_related('service').order_by('-id')

    if statuses:
        orders = orders.filter(status__in=statuses)

    if payment_statuses:
        if payment_statuses == [OrderReportForm.PAYMENT_STATUS.paid,
                                OrderReportForm.PAYMENT_STATUS.credit]:
            orders = orders

        elif OrderReportForm.PAYMENT_STATUS.paid in payment_statuses:
            orders = orders.filter(completed_paid=True)

        elif OrderReportForm.PAYMENT_STATUS.credit in payment_statuses:
            orders = orders.filter(completed_paid=False)

    for order in orders:
        total_visit = order.bookings.exclude(status=Booking.STATUS.canceled).count()
        payment_status = "Completed " if order.completed_paid else "Credit"
        row_content = [order.code,
                       order.user.name,
                       order.created.strftime('%Y/%m/%d %H:%M'),
                       order.service.name,
                       order.get_status_display(),
                       order.price,
                       order.promotion_code,
                       order.discount,
                       order.discounted_price,
                       "%s of %s visit" % (total_visit, order.service.number_of_visit),
                       payment_status]
        rows.append(row_content)

    return rows


def get_balance_to_use(price, user):
    if user.balance >= price:
        return price
    return user.balance
