from django.conf.urls import url

from .views import add, index, detail, status


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^add$', add, name='add'),
    url(r'^status$', status, name='status'),
    url(r'^(?P<id>\d+)/detail$', detail, name='detail'),
]
