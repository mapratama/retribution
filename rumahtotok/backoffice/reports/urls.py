from django.conf.urls import url

from .views import index, bookings, orders, payments


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^bookings/$', bookings, name='bookings'),
    url(r'^orders/$', orders, name='orders'),
    url(r'^payments/$', payments, name='payments')
]
