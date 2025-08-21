# accounts/urls.py
from django.urls import path
from .views import SmartSendCodeView, VerifyEmailCodeView

urlpatterns = [
    path('auth/send-code/', SmartSendCodeView.as_view(), name='send-code'),
    path('auth/verify-code/', VerifyEmailCodeView.as_view(), name='verify-code'),
]

