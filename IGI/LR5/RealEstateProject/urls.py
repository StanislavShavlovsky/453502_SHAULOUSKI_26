from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Built-in Django administration control panel
    path('admin/', admin.site.urls),

    # Delegate route evaluation to the local application routing table
    path('', include('agency.urls')),
]

# Serve media assets locally if running inside a development environment
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)