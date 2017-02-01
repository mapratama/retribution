from django.conf.urls import url

from .views import Preview, Create, Review, Cancel, Edit

urlpatterns = [
    url(r'^preview/$', Preview.as_view(), name='preview'),
    url(r'^create/$', Create.as_view(), name='create'),
    url(r'^review/$', Review.as_view(), name='review'),
    url(r'^cancel/$', Cancel.as_view(), name='cancel'),
    url(r'^edit/$', Edit.as_view(), name='edit'),
]
