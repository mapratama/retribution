from django.conf.urls import url

from .views import StoreList

urlpatterns = [
    url(r'^$', StoreList.as_view(), name='index'),
]
