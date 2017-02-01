import calendar

from django.conf import settings


def serialize_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'birthday': user.birthday.isoformat() if user.birthday else None,
        'gender': user.get_gender_display(),
        'mobile_number': user.mobile_number,
        'email': user.email,
        'balance': user.balance
    }


def serialize_treatment(treatment):
    photo_url = settings.HOST + treatment.photo.thumbnails.get('source_300').url \
        if treatment.photo else None

    icon_url = settings.HOST + treatment.icon.thumbnails.get('source_300').url \
        if treatment.icon else None

    return {
        'id': treatment.id,
        'name': treatment.name,
        'description': treatment.description,
        'photo': photo_url,
        'icon': icon_url,
        'is_active': treatment.is_active,
        'position': treatment.position,
        'services': [serialize_service(service) for service in treatment.services.all()]
    }


def serialize_service(service):
    return {
        'id': service.id,
        'name': service.name,
        'time_needed': service.time_needed,
        'price': service.price,
        'discounted_price': service.discounted_price,
        'number_of_visit': service.number_of_visit,
        'number_of_people': service.number_of_people,
        'description': service.description,
        'is_active': service.is_active,
        'max_booking': service.max_booking
    }


def serialize_store(store):
    photo_url = settings.HOST + store.photo.thumbnails.get('source_300').url \
        if store.photo else None

    return {
        'id': store.id,
        'name': store.name,
        'address': store.address,
        'bbm_pin': store.BBM_pin if store.BBM_pin else None,
        'phone': store.phone if store.phone else None,
        'photo_url': photo_url,
        'is_active': store.is_active,
        'lat': store.lat,
        'long': store.long
    }


def serialize_banner(banner):

    return {
        'image1': settings.HOST + banner.image1.url if banner.image1 else None,
        'image2': settings.HOST + banner.image2.url if banner.image2 else None,
        'image3': settings.HOST + banner.image3.url if banner.image3 else None,
        'image4': settings.HOST + banner.image4.url if banner.image4 else None,
    }


def serialize_order(order):
    return {
        'id': order.id,
        'code': order.code,
        'created': calendar.timegm(order.created.utctimetuple()),
        'price': order.price,
        'unique_price': order.unique_price,
        'status': order.status,
        'service': serialize_service(order.service),
        'discount': order.discount,
        'promotion_code': order.promotion_code,
        'completed_paid': order.completed_paid,
        'balance_reversed': order.balance_reversed,
        'total_booking': order.total_booking,
        'can_booking': True if order.total_booking < order.service.max_booking else False,
        'completed_booking': order.completed_booking,
        'can_canceled': order.can_canceled(),
        'total_payment': order.total_payment,
        'bookings': [serialize_booking(booking) for booking in order.bookings.order_by('-id')],
        'payment_confirmations': [serialize_payment_confirmation(p)
                                  for p in order.payment_confirmations.all()]
    }


def serialize_payment_confirmation(payment_confirmation):
    photo_url = settings.HOST + payment_confirmation.photo.thumbnails.get('size_500').url \
        if payment_confirmation.photo else None

    return {
        'id': payment_confirmation.id,
        'order_code': payment_confirmation.order.code,
        'status': payment_confirmation.status,
        'created': calendar.timegm(payment_confirmation.created.utctimetuple()),
        'photo_url': payment_confirmation.photo_url,
        'photo': photo_url,
        'value': payment_confirmation.value,
        'notes': payment_confirmation.notes,
    }


def serialize_payment(payment):
    return {
        'id': payment.id,
        'code': payment.code,
        'created': calendar.timegm(payment.time.utctimetuple()),
        'balance_used': payment.balance_used,
        'value': payment.value,
        'notes': payment.notes,
    }


def serialize_booking(booking):
    return {
        'id': booking.id,
        'code': booking.code,
        'created': calendar.timegm(booking.created.utctimetuple()),
        'status': booking.status,
        'store': serialize_store(booking.store),
        'duration': booking.duration,
        'notes': booking.notes,
        'date': booking.date.isoformat(),
        'therapist': serialize_therapist(booking.therapist) if booking.therapist else None,
        'rating': booking.rating,
        'review': booking.review
    }


def serialize_therapist(therapist):
    photo_url = settings.HOST + therapist.photo.thumbnails.get('size_500').url \
        if therapist.photo else None

    return {
        'id': therapist.id,
        'name': therapist.user.name,
        'photo_url': photo_url,
    }
