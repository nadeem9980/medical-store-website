from django.contrib import admin
from django.urls import path
from django.urls import include
import django.contrib.auth.views as auth_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("Pharmacy.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
