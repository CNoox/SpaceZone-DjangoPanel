from django.urls import path
from rest_framework import routers
from .views import ProductViewSet,CommentViewsSet,CategoryView,CategoryProductView

comment_by_slug = CommentViewsSet.as_view({'get': 'retrieve'})
edit_comment_by_id = CommentViewsSet.as_view({'patch':'partial_update'})

urlpatterns = [
    path('comments/<str:slug>/', comment_by_slug, name='comments-by-slug'),
    path('comments/<str:slug>/<int:pk>/',edit_comment_by_id,name='edit-comment-by-id'),
    path('category/',CategoryView.as_view(),name='categories'),
    path('category/<str:slug>/', CategoryProductView.as_view(), name='category-product'),
]

router_product = routers.SimpleRouter()
router_product.register('product', ProductViewSet)
urlpatterns += router_product.urls
