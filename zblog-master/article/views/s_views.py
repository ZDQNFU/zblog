from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from article.models import Article, Category, Tag, Comment
from article.serializers.article_serializer import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleWriteSerializer,
    CategorySerializer,
    TagSerializer,
    CommentAdminSerializer,
)


# ---------- Article CRUD ----------

class SArticleListCreateView(generics.ListCreateAPIView):
    """S端：文章列表 & 创建"""
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'content_md', 'author__username']
    queryset = (
        Article.objects
        .select_related('author', 'category')
        .prefetch_related('tags')
        .order_by('-created_at')
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ArticleListSerializer
        return ArticleWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """S端：文章详情 & 更新 & 删除"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return (
            Article.objects
            .select_related('author', 'category')
            .prefetch_related('tags')
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ArticleDetailSerializer
        return ArticleWriteSerializer


# ---------- Tag CRUD ----------

class STagListCreateView(generics.ListCreateAPIView):
    """S端：标签列表 & 创建"""
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    queryset = Tag.objects.order_by('-created_at')
    serializer_class = TagSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class STagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """S端：标签详情 & 更新 & 删除"""
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ---------- Category CRUD ----------

class SCategoryListCreateView(generics.ListCreateAPIView):
    """S端：分类列表 & 创建"""
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    queryset = Category.objects.order_by('-created_at')
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class SCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """S端：分类详情 & 更新 & 删除"""
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# ---------- Comment CRUD ----------

class SCommentListCreateView(generics.ListCreateAPIView):
    """S端：评论列表"""
    permission_classes = [IsAuthenticated]
    search_fields = ['author__username', 'content']
    queryset = (
        Comment.objects
        .select_related('author', 'article')
        .order_by('-created_at')
    )
    serializer_class = CommentAdminSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SCommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """S端：评论详情 & 更新 & 删除"""
    permission_classes = [IsAuthenticated]
    queryset = (
        Comment.objects
        .select_related('author', 'article')
    )
    serializer_class = CommentAdminSerializer
