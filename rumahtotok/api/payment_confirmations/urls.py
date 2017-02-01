from django.conf.urls import url

from .views import Add, Details

urlpatterns = [
    url(r'^add/$', Add.as_view(), name='add'),
    url(r'^(?P<id>\d+)$', Details.as_view(), name='details'),
]
