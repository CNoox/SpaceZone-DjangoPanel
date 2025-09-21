from django.urls import path
from .views import AdminSendCodeView,AdminPanelView,AdminVerifyCodeView,UserInformationViewSet
from rest_framework import routers


urlpatterns = [
    path('admin/send-code/',AdminSendCodeView.as_view(),name='admin-send-code'),
    path('admin/verify-code/',AdminVerifyCodeView.as_view(),name='admin-verify-code'),
    path('admin/panel/',AdminPanelView.as_view(),name='admin-panel')
]
router = routers.SimpleRouter()
router.register('admin/panel/users',UserInformationViewSet)
urlpatterns += router.urls