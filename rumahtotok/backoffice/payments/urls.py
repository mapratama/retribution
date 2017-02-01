from django.conf.urls import url

from .views import add, detail


urlpatterns = [
    url(r'^(?P<order_id>\d+)/add$', add, name='add'),
    url(r'^(?P<payment_id>\d+)/detail$', detail, name='detail'),
]
