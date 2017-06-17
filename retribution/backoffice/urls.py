from django.conf.urls import url, include

from .views import login_view, log_out, index


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^login$', login_view, name='login'),
    url(r'^log_out$', log_out, name='log_out'),
    url(r'^customers/', include('retribution.backoffice.customers.urls', namespace='customers')),
    url(r'^destinations/', include('retribution.backoffice.destinations.urls', namespace='destinations')),
    url(r'^employees/', include('retribution.backoffice.employees.urls', namespace='employees')),
    url(r'^retributions/', include('retribution.backoffice.retributions.urls', namespace='retributions')),
]
