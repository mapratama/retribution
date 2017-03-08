from django.conf.urls import include, url

urlpatterns = [
    url(r'^auth/', include('rumahtotok.api.auth.urls', namespace='auth')),
    url(r'^bookings/', include('rumahtotok.api.bookings.urls', namespace='bookings')),
    url(r'^orders/', include('rumahtotok.api.orders.urls', namespace='orders')),
    url(r'^stores/', include('rumahtotok.api.stores.urls', namespace='stores')),
    url(r'^payment-confirmations/', include(
    	'rumahtotok.api.payment_confirmations.urls', namespace='payment_confirmations')),
    url(r'^treatments/', include('rumahtotok.api.treatments.urls', namespace='treatments')),
    url(r'^home/', include('rumahtotok.api.home.urls', namespace='home')),
    url(r'^users/', include('rumahtotok.api.users.urls', namespace='users')),
    url(r'^vouchers/', include('rumahtotok.api.vouchers.urls', namespace='vouchers')),
    url(r'^wallets/', include('rumahtotok.api.wallets.urls', namespace='wallets')),
    url(r'^redemptions/', include('rumahtotok.api.redemptions.urls', namespace='redemptions')),
]
