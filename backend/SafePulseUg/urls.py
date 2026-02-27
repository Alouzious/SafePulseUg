from django.contrib             import admin
from django.urls                import path, include
from django.conf                import settings
from django.conf.urls.static    import static
from drf_spectacular.views      import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # ── Django Admin ────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── API Documentation ───────────────────────────────────
    path('api/schema/',  SpectacularAPIView.as_view(),         name='schema'),
    path('api/docs/',    SpectacularSwaggerView.as_view(
                            url_name='schema'
                         ),                                    name='swagger-ui'),
    path('api/redoc/',   SpectacularRedocView.as_view(
                            url_name='schema'
                         ),                                    name='redoc'),

    # ── App API Routes ──────────────────────────────────────
    path('api/auth/',       include('apps.accounts.urls')),
    path('api/crimes/',     include('apps.crimes.urls')),
    path('api/analysis/',   include('apps.analysis.urls')),
    path('api/reports/',    include('apps.reports.urls')),
    path('api/dashboard/',  include('apps.dashboard.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)