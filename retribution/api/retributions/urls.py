from django.conf.urls import patterns, url

from .views import Add


urlpatterns = patterns('',
    url(r'^add$', Add.as_view(), name='add'),
)
