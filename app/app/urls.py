from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ======= Accounts URL's ======= #
    path('accounts/', include('accounts.urls')),

    # ======= Accounts URL's ======= #
    path('forms/', include('forms.urls')),

    # ========== API schema generator ========== #
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/', SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
