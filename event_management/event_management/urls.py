"""Event management URL Configuration."""

from django.contrib import admin
from django.urls import include, path

from rest_framework.authtoken import views

from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/events/", include("event.urls")),
    path("api/users/", include("user.urls")),
    path("api-token-auth/", views.obtain_auth_token),
]


urlpatterns += doc_urls
