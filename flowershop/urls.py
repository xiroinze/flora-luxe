from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

# Медиа-файлы: в продакшене нужен nginx/S3, но для Railway без CDN — раздаём через Django
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Статика в dev режиме
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
