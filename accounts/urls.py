# accounts/urls.py
from django.urls import path
from .views import SmartSendCodeView, VerifyEmailCodeView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="""
My API provides a complete set of endpoints for authentication, user management, 
and data operations. Designed with clarity and simplicity, this API allows developers 
to quickly explore, test, and integrate features in a structured and interactive way. 

- Fully documented with request and response examples
- Supports JWT authentication for secure access
- Compatible with OpenAPI 3.0 standards
- Ideal for both frontend and backend integration
""",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('auth/send-code/', SmartSendCodeView.as_view(), name='send-code'),
    path('auth/verify-code/', VerifyEmailCodeView.as_view(), name='verify-code'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
