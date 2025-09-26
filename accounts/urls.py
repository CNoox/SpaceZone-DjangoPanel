from django.urls import path
from .views import UserVerifyCodeView,UserSendCodeView,UserPanelView,SendCodeForgetUserView ,UpdatePasswordView,LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('auth/send-code/', UserSendCodeView.as_view(), name='user-send-code'),
    path('auth/verify-code/', UserVerifyCodeView.as_view(), name='user-verify-code'),
    path('auth/panel/',UserPanelView.as_view(),name='user-panel'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Optional UI:
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('auth/forget/',SendCodeForgetUserView.as_view(),name='forget_password'),
    path('auth/forget/set/',UpdatePasswordView.as_view(),name='set_password'),

    path('logout/',LogoutView.as_view(),name='logout')
]
