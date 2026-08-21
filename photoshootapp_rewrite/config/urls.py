"""
Main URL Configuration for PhotoshootApp
Clean, namespaced routing structure
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # App URLs (namespaced)
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('events/', include('apps.events.urls', namespace='events')),
    path('gallery/', include('apps.media_library.urls', namespace='media_library')),
    path('ai/', include('apps.ai_engine.urls', namespace='ai_engine')),
    path('store/', include('apps.store.urls', namespace='store')),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error pages
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
