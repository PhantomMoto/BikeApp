from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),  # your app urls
]

# Serve media files in development and Render server:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Render doesn't serve media automatically in production, you need to configure a web server or use django-storages etc.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
