import calendar

from django.db.models import Sum
from django.utils.timezone import localtime

from retribution.apps.retributions.models import Retribution


def sync():
    retribution_data = []
    retributions = Retribution.objects.filter(has_submitted=False)\
        .select_related('destination', 'created_by')
    for retribution in retributions:
        data = {
            "id": retribution.id,
            "destination": retribution.destination.id,
            "qr_code": retribution.qr_code,
            "type": retribution.type,
            "quantity": retribution.quantity,
            "price": retribution.price,
            "created_by": retribution.created_by.id,
            'created': calendar.timegm(retribution.created.utctimetuple()),
            "transport": retribution.transport or None,
            "transport_id": retribution.transport_id or None,
            "mobile_number": retribution.mobile_number or None,
            "email": retribution.email or None,
        }

        retribution_data.append(data)


def generate_report(retributions, start_date, end_date):
    rows = []


    total_retribution = retributions.count(),
    total_customer = retributions.aggregate(Sum('quantity'))['quantity__sum'] or 0,
    total_transaction = retributions.aggregate(Sum('price'))['price__sum'] or 0,

    for retribution in retributions:
        row_content = [retribution.qr_code,
                       retribution.destination.name,
                       retribution.get_type_display(),
                       retribution.get_transport_display() if retribution.get_transport_display() else "-",
                       localtime(retribution.created).strftime('%d/%m/%Y, %H:%M'),
                       retribution.quantity,
                       retribution.price]

        rows.append(row_content)

    rows.append('')
    if start_date and end_date:
        rows.append(['Start:', start_date.strftime('%Y/%m/%d'),
                     'End:', end_date.strftime('%Y/%m/%d')])
    rows.append(['Total Retribution', total_retribution[0]])    
    rows.append(['Total Customer', total_customer[0]])    
    rows.append(['Total Transaction', total_transaction[0]])    

    return rows