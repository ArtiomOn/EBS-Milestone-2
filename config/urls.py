from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Enjoy",
    ),
    public=True,
    permission_classes=[AllowAny]
)

# noinspection PyUnresolvedReferences
urlpatterns = [
    path("", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('auth/', admin.site.urls),
    path('', include('apps.tasks.urls')),
    path('users/', include("apps.users.urls")),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns
