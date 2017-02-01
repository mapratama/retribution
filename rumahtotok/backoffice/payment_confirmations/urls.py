from django.conf.urls import url

from .views import index, verified


urlpatterns = [
    url(r'^index/$', index, name='index'),
    url(r'^(?P<id>\d+)/verified$', verified, name='verified'),
]
