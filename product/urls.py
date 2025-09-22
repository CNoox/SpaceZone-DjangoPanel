from django.urls import path
from rest_framework import routers
from .views import ProductViewSet,CommentViewsSet

comment_by_slug = CommentViewsSet.as_view({'get': 'retrieve'})

urlpatterns = [
    path('comments/<str:slug>/', comment_by_slug, name='comments-by-slug')
]

router_product = routers.SimpleRouter()
router_product.register('product', ProductViewSet)
urlpatterns += router_product.urls
