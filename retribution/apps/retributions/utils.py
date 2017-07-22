import calendar

from django.conf import settings

from retribution.apps.retributions.models import Retribution
from retribution.core.utils import api_call


def sync():
    retributions_data = []
    retributions = Retribution.objects.filter(has_submitted=False)\
        .select_related('destination', 'created_by')
    for retribution in retributions:
        data = {
            "id": retribution.id,
            "destination": retribution.destination.id,
            "qr_code": str(retribution.qr_code),
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

        retributions_data.append(data)

    url = settings.BASE_URL + "/retributions/add"
    payloads = {
        'token': settings.TOKEN,
        'retributions': retributions_data
    }

    response = api_call('POST', url, payloads)
    if response['status_code'] == 200:
        retributions.update(has_submitted=True)
