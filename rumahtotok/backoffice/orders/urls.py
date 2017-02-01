from django.conf.urls import url

from .views import add, index, detail, cancel, reverse_balance, invoice_print


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^add$', add, name='add'),
    url(r'^(?P<id>\d+)/detail$', detail, name='detail'),
    url(r'^(?P<id>\d+)/reverse-balance$', reverse_balance, name='reverse_balance'),
    url(r'^(?P<id>\d+)/cancel$', cancel, name='cancel'),
    url(r'^(?P<id>\d+)/print$', invoice_print, name='invoice_print'),
]
