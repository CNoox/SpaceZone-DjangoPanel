from django.urls import path
from .views import OrderView,AddItemView,SubItemView,DeleteItemView

urlpatterns = [
    path('auth/panel/order/',OrderView.as_view(),name='order'),
    path('auth/panel/order/add-items/', AddItemView.as_view(), name='add-item'),
    path('auth/panel/order/sub-items/',SubItemView.as_view(), name='sub-item'),
    path('auth/panel/order/del-items/<int:pk>/',DeleteItemView.as_view(),name='del-item')
]