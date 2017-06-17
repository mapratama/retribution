from django.conf.urls import url

from .views import add, index, edit_destination, detail


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^add$', add, name='add'),
    url(r'^(?P<id>\d+)/edit-destination$', edit_destination, name='edit_destination'),
    url(r'^(?P<id>\d+)/detail$', detail, name='detail'),
]
