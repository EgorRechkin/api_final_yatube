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
        return Response(serializer.data)

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
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.author != request.user:
            return Response(
                {"detail":
                    "У вас недостаточно прав для выполнения этого действия."},
                status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail":
                    'У вас недостаточно прав для выполнения данного действия.'
                 }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
