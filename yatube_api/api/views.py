from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.exceptions import (
    PermissionDenied, ValidationError, NotFound)
from posts.models import Post, Follow, Group, Comment
from .serializers import (
    PostSerializer, CommentSerializer, FollowSerializer, GroupSerializer)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def check_author_permission(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied(
                "У вас недостаточно прав для выполнения данного действия.")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_author_permission(instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_author_permission(instance)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(post=post, author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        comment_id = self.kwargs.get('pk')
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = self.get_serializer(comment)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=self.kwargs.get('pk'))
        serializer = self.get_serializer(comment,
                                         data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied(
                "У вас недостаточно прав для редактирования комментария.")
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied(
                "У вас недостаточно прав для выполнения данного действия.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise NotFound(
                "У вас недостаточно прав для выполнения данного действия.")
        queryset = Follow.objects.filter(user=self.request.user)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                following__username__icontains=search_query)
        return queryset

    def perform_create(self, serializer):
        following_user = serializer.validated_data['following']
        if following_user == self.request.user:
            raise ValidationError("Нельзя подписаться на самого себя.")
        if Follow.objects.filter(user=self.request.user,
                                 following=following_user).exists():
            raise ValidationError("Вы уже подписаны на этого пользователя.")
        serializer.save(user=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    http_method_names = ['get', 'head', 'options']
