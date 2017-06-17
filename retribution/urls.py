from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^backoffice/', include('retribution.backoffice.urls', namespace='backoffice')),
]

if settings.DEBUG:
    urlpatterns.append(url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {  # noqa
            'document_root': settings.MEDIA_ROOT,
        }),
   )
