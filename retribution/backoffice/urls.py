from django.conf.urls import url, include

from .views import login_view, log_out, index, create


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^login$', login_view, name='login'),
    url(r'^log_out$', log_out, name='log_out'),
    url(r'^create$', create, name='create'),
    url(r'^users/', include('retribution.backoffice.users.urls', namespace='users')),
    url(r'^destinations/', include('retribution.backoffice.destinations.urls', namespace='destinations')),
    url(r'^retributions/', include('retribution.backoffice.retributions.urls', namespace='retributions')),
]
