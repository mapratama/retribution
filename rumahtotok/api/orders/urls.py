from django.conf.urls import url

from .views import (OrderList, Create, OrderDetail, ValidatePromotion,
                    Cancel)

urlpatterns = [
    url(r'^$', OrderList.as_view(), name='index'),
    url(r'^create/$', Create.as_view(), name='create'),
    url(r'^validate-promotion/$', ValidatePromotion.as_view(), name='validate_promotion'),
    url(r'^(?P<order_id>\d+)$', OrderDetail.as_view(), name='details'),
    url(r'^cancel/$', Cancel.as_view(), name='cancel'),
]
