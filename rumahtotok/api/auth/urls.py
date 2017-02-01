from django.conf.urls import url

from .views import Login, Logout, Register, GetConfirmationCode, ResetPassword

urlpatterns = [
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^get-confirmation-code/$', GetConfirmationCode.as_view(), name='get_confirmation_code'),
    url(r'^reset-password/$', ResetPassword.as_view(), name='reset_password')
]
