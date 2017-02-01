from django.conf.urls import url, include

from .views import login_view, log_out, index


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^login$', login_view, name='login'),
    url(r'^log_out$', log_out, name='log_out'),
    url(r'^balances/', include('rumahtotok.backoffice.balances.urls', namespace='balances')),
    url(r'^bookings/', include('rumahtotok.backoffice.bookings.urls', namespace='bookings')),
    url(r'^customers/', include('rumahtotok.backoffice.customers.urls', namespace='customers')),
    url(r'^payment-confirmations/', include('rumahtotok.backoffice.payment_confirmations.urls', 
                                            namespace='payment_confirmations')),
    url(r'^orders/', include('rumahtotok.backoffice.orders.urls', namespace='orders')),
    url(r'^services/', include('rumahtotok.backoffice.services.urls', namespace='services')),
    url(r'^payments/', include('rumahtotok.backoffice.payments.urls', namespace='payments')),
    url(r'^promotions/', include('rumahtotok.backoffice.promotions.urls', namespace='promotions')),
    url(r'^reports/', include('rumahtotok.backoffice.reports.urls', namespace='reports')),
    url(r'^stores/', include('rumahtotok.backoffice.stores.urls', namespace='stores')),
    url(r'^therapists/', include('rumahtotok.backoffice.therapists.urls', namespace='therapists')),
    url(r'^treatments/', include('rumahtotok.backoffice.treatments.urls', namespace='treatments')),
]
