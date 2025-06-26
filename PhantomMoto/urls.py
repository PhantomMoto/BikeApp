from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from products.models import Accessory  # ya jo bhi model tu sitemap me dikhana chahta hai
# from django.urls import path
from django.views.generic import TemplateView

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'products', 'contact', 'blogs', 'login', 'register']

    def location(self, item):
        return '/' if item == 'home' else f'/{item}/'

class AccessorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Accessory.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # ya obj.created_at agar updated field nai hai

sitemaps = {
    'static': StaticViewSitemap,
    'accessories': AccessorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),  # your app urls
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media files in development and Render server:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Render doesn't serve media automatically in production, you need to configure a web server or use django-storages etc.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.views.generic import TemplateView

urlpatterns += [
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]