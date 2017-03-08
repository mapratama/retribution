from django.conf.urls import patterns, url

from .views import Created


urlpatterns = patterns('',
    url(r'^created$', Created.as_view(), name='created'),
)
