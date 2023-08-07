from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static

from conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('parser_books.urls', namespace='books_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    from django.conf.urls.static import static
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view
    from rest_framework import permissions
    import debug_toolbar

    schema_view = get_schema_view(
        openapi.Info(
            title="Telegram Books API",
            default_version='0.1.0',
            description="Документация API",
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns.extend(
        [
            re_path(
                r'^doc(?P<format>\.json|\.yaml)$',
                schema_view.without_ui(cache_timeout=0),
                name='schema-json',
            ),
            path(
                'doc/',
                schema_view.with_ui('swagger', cache_timeout=0),
                name='schema-swagger-ui',
            ),
            path(
                'redoc/',
                schema_view.with_ui('redoc', cache_timeout=0),
                name='schema-redoc',
            ),
        ]
    )

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
