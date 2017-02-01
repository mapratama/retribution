from django.conf.urls import url

from .views import add, edit, detail


urlpatterns = [
    url(r'^(?P<treatment_id>\d+)/add$', add, name='add'),
    url(r'^(?P<service_id>\d+)/edit$', edit, name='edit'),
    url(r'^(?P<service_id>\d+)/detail$', detail, name='detail'),
]
