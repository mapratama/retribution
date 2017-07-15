from django.conf.urls import url

from .views import add, index, edit, detail


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^add$', add, name='add'),
    url(r'^(?P<id>\d+)/edit$', edit, name='edit'),
    url(r'^(?P<id>\d+)/detail$', detail, name='detail'),
]
