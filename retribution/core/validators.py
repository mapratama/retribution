from django.core.exceptions import ValidationError

from id_phonenumbers import parse
from phonenumbers import phonenumberutil
from django.core.validators import validate_email as django_validate_email


def validate_mobile_number(phone_number):
    try:
        number = parse(phone_number)
    except phonenumberutil.NumberParseException:
        raise ValidationError('Please enter a valid mobile phone number.')

    if number.is_mobile:
        return True

    raise ValidationError('Please enter a valid mobile phone number.')


def validate_email_address(email):
    django_validate_email(email)

    if email.endswith('.'):
        raise ValidationError('Email cannot end with \'.\' (dot), please check again')
    else:
        return True