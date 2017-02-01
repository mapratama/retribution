import json

from django.core.urlresolvers import reverse
from django.test import TestCase


class RumahTotokTestCase(TestCase):

    headers = {
        'content_type': 'application/json',
        'wsgi.url_scheme': 'https'
    }
    token = 'hjt573v3863hjkagg2ffgmllauey8832bndab'

    def get_session_key(self, username, password):
        data = {
            "username": username,
            "password": password,
            "token": self.token
        }
        response = self.client.post(reverse('api:auth:login'),
                                    json.dumps(data), **self.headers)
        return json.loads(response.content)['session_key']
