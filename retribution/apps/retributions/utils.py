import calendar

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
