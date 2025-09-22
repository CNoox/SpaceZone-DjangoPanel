from django.urls import path
from .views import AdminSendCodeView,AdminPanelView,AdminVerifyCodeView,UserInformationViewSet,ProductInformationViewSet,AdminCategoryViewSet,AdminSelectCategoryViewSet
from rest_framework import routers

urlpatterns = [
    path('admin/send-code/',AdminSendCodeView.as_view(),name='admin-send-code'),
    path('admin/verify-code/',AdminVerifyCodeView.as_view(),name='admin-verify-code'),
    path('admin/panel/',AdminPanelView.as_view(),name='admin-panel')
]
router_user = routers.SimpleRouter()
router_user.register('admin/panel/users',UserInformationViewSet)

router_product = routers.SimpleRouter()
router_product.register('admin/panel/product',ProductInformationViewSet)

router_category = routers.SimpleRouter()
router_category.register('admin/panel/category',AdminCategoryViewSet)

router_select_category = routers.SimpleRouter()
router_select_category.register('admin/category/select',AdminSelectCategoryViewSet)

urlpatterns += router_user.urls + router_product.urls + router_category.urls + router_select_category.urls