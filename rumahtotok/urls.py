from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^backoffice/', include('rumahtotok.backoffice.urls', namespace='backoffice')),
    url(r'^api/', include('rumahtotok.api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns.append(url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {  # noqa
            'document_root': settings.MEDIA_ROOT,
        }),
   )
