from django.urls import path
from .views import UserVerifyCodeView,UserSendCodeView,UserPanelView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('auth/send-code/', UserSendCodeView.as_view(), name='send-code'),
    path('auth/verify-code/', UserVerifyCodeView.as_view(), name='verify-code'),
    path('panel/',UserPanelView.as_view(),name='user-panel'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
