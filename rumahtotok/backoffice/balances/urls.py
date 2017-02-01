from django.conf.urls import url

from .views import add, details

urlpatterns = [
    url(r'^(?P<customer_id>\d+)/add$', add, name='add'),
    url(r'^(?P<id>\d+)/details$', details, name='details'),
]
