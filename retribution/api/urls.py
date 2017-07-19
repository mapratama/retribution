from django.conf.urls import include, patterns, url


urlpatterns = patterns('retribution.api.views',
    url(r'^auth/', include('retribution.api.auth.urls', namespace='auth')),
    url(r'^retributions/', include('retribution.api.retributions.urls', namespace='retributions')),
)
