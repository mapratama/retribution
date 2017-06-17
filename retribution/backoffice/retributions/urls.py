from django.conf.urls import url

from .views import add, index, detail


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^add$', add, name='add'),
    url(r'^(?P<id>\d+)/detail$', detail, name='detail'),
]
