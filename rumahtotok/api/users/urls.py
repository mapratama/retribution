from django.conf.urls import url

from .views import UserDetail, ChangeProfile

urlpatterns = [
    url(r'^$', UserDetail.as_view(), name='detail'),
    url(r'^change-profile$', ChangeProfile.as_view(), name="change_profile"),
]
