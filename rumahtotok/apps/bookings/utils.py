from rumahtotok.apps.bookings.models import Booking
from rumahtotok.core.utils import prepare_datetime_range


def generate_booking_report(start_date, end_date, store=None, therapist=None):
    rows = []
    rows.append(['Start:', start_date.strftime('%Y/%m/%d'),
                 'End:', end_date.strftime('%Y/%m/%d')])
    rows.append('')
    header = (
        'Code',
        'Store',
        'Date',
        'Customer Name',
        'Therapist Name',
        'Status',
        'Rating',
    )
    rows.append(header)
    start_date, end_date = prepare_datetime_range(start_date, end_date)
    bookings = Booking.objects.exclude(status=Booking.STATUS.canceled) \
        .select_related('order__user').filter(date__range=(start_date, end_date))\
        .order_by('date')

    if store:
        bookings = bookings.filter(store=store)

    if therapist:
        bookings = bookings.filter(therapist=therapist)

    for booking in bookings:
        row_content = [booking.code,
                       booking.store,
                       booking.date.strftime('%Y/%m/%d'),
                       booking.order.user.name,
                       booking.therapist,
                       booking.get_status_display(),
                       booking.get_rating_display()]

        rows.append(row_content)

    return rows
