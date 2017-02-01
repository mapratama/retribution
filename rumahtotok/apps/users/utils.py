
import django_rq
from django.conf import settings

from gcm import GCM
from gcm.gcm import GCMInvalidRegistrationException, GCMNotRegisteredException


def send_android_push_notification(user, title, body, extra_data=None, async=True):
    gcm = GCM(settings.GOOGLE_API_KEY)
    data = {'body': body, 'title': title, 'extra_data': extra_data}

    if settings.TEST:
        return

    if not user.gcm_key:
        return

    reg_id = [user.gcm_key]

    kwargs = {
        "data": data,
        "registration_ids": reg_id,
    }

    try:
        if async:
            django_rq.enqueue(gcm.json_request, **kwargs)
        else:
            gcm.json_request(**kwargs)
    except (GCMInvalidRegistrationException, GCMNotRegisteredException):
        return
