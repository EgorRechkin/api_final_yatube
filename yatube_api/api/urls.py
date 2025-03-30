from rest_framework import routers
from django.urls import include, path

from .views import PostViewSet, CommentViewSet

router = routers.DefaultRouter()

router.register('posts', PostViewSet, basename='posts')
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/posts/<int:post_id>/comments/',
         CommentViewSet.as_view({
             'get': 'list',
             'post': 'create'}), name='comments-list'),
    path('v1/posts/<int:post_id>/comments/<int:pk>/',
         CommentViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }), name='comments-detail'),
]
