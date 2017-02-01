from django.conf.urls import url

from .views import (index, add, edit, detail, cancel, set_completed)


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^(?P<order_id>\d+)/add$', add, name='add'),
    url(r'^(?P<id>\d+)/edit$', edit, name='edit'),
    url(r'^(?P<id>\d+)/detail$', detail, name='detail'),
    url(r'^(?P<booking_id>\d+)/cancel$', cancel, name='cancel'),
    url(r'^(?P<booking_id>\d+)/set-completed$', set_completed, name='set_completed'),
]
