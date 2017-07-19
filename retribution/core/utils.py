from datetime import datetime as _datetime

import os
import unicodecsv
import zipfile
import json
import requests
import phonenumbers

from hashids import Hashids
from io import BytesIO

from requests.exceptions import RequestException

from django.contrib.auth import login
from django.http import HttpResponse
from django.utils import timezone
from django.template.defaultfilters import slugify

from .exceptions import RetributionAPIError


class FilenameGenerator(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, instance, filename):
        today = timezone.localtime(timezone.now()).date()

        filepath = os.path.basename(filename)
        filename, extension = os.path.splitext(filepath)
        filename = slugify(filename)

        path = "/".join([
            self.prefix,
            str(today.year),
            str(today.month),
            str(today.day),
            filename + extension
        ])
        return path


try:
    from django.utils.deconstruct import deconstructible
    FilenameGenerator = deconstructible(FilenameGenerator)
except ImportError:
    pass


def normalize_phone(number):
    number = number[1:] if number[:1] == '0' else number
    parse_phone_number = phonenumbers.parse(number, 'ID')
    phone_number = phonenumbers.format_number(
        parse_phone_number, phonenumbers.PhoneNumberFormat.E164)
    return phone_number


def datetime(*args, **kwargs):
    time = _datetime(*args, **kwargs)
    if 'tzinfo' not in kwargs:
        time = timezone.make_aware(time)
    return time


def generate_hashids(id, length=5, prefix=''):
    hashids = Hashids(min_length=length, alphabet='123456789ABCDEFGHJKLMNPQRSTUWXYZ')
    return hashids.encode(id)


def prepare_datetime_range(start, end, tzinfo=None):
    start = _datetime.combine(start, _datetime.min.time())
    start = timezone.localtime(timezone.make_aware(start))
    end = _datetime.combine(end, _datetime.max.time())
    end = timezone.localtime(timezone.make_aware(end))

    return start, end


def prepare_start_date(date, tzinfo=None):
    start = _datetime.combine(date, _datetime.min.time())
    start = timezone.localtime(timezone.make_aware(start))
    return start


def prepare_end_date(date, tzinfo=None):
    end = _datetime.combine(date, _datetime.max.time())
    end = timezone.localtime(timezone.make_aware(end))

    return end


def force_login(request, user):
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)


class Page(object):
    def __init__(self, queryset, page_number=1, step=20):
        page_number = int(page_number)
        self.next = None
        self.next_object = None

        # We want our implementation of pagination to have access
        # to both previous and next object.

        stop_index = (page_number * step) + 1

        # If we're not in the first page, fetch the previous item
        # in addition to fetching the next item
        if page_number > 1:
            start_index = (page_number - 1) * step - 1

            queryset = list(queryset[start_index:stop_index])
            self.previous = page_number - 1

            # even when number is bigger than possible, no errors are produced
            if len(queryset):
                self.previous_object = queryset[0]
            else:
                self.previous_object = None
            self.objects = queryset[1:step + 1]

            # If the number of result is two more than number
            # of objects in a page, there's a next page
            if len(queryset) == step + 2:
                self.next_object = queryset[-1]
                self.next = page_number + 1

        else:
            self.previous = None
            self.previous_object = None
            start_index = (page_number - 1) * step
            queryset = list(queryset[start_index:stop_index])

            # If the number of result is more than number of objects
            # in page, we know there's a next page
            if len(queryset) > step:
                self.next = page_number + 1
                self.next_object = queryset[-1]

            self.objects = queryset[0:step]


def zip_response(zip_buffer, filename):
    response = HttpResponse(zip_buffer.getvalue(),
                            content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % filename

    return response


def generate_zip_report(report, file_name):
    zip_buffer = BytesIO()
    csv_buffer = BytesIO()
    writer = unicodecsv.writer(csv_buffer, encoding='utf-8')
    for row in report:
        writer.writerow(row)

    with zipfile.ZipFile(zip_buffer, mode='w') as zip_file:
        zip_file.writestr(file_name + '.csv', csv_buffer.getvalue())

    return zip_response(zip_buffer, file_name)


def api_call(request_type, url, payloads):
    try:
        if request_type == 'GET':
            response = requests.get(url, params=payloads)
        if request_type == 'POST':
            response = requests.post(url, json=payloads)
    except RequestException as Error:
        raise RetributionAPIError(Error)

    response_dict = json.loads(response.text)
    response_dict['status_code'] = response.status_code
    return response_dict
