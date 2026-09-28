from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

urlpatterns = [
    # Built-in Django administration control panel
    path('admin/', admin.site.urls),

    # Delegate route evaluation to the local application routing table
    path('', include('agency.urls')),
]


if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]


