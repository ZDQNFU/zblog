from rest_framework import serializers

from article.models import (
    Article,
    Category,
    Tag,
    Comment,
    Like
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author_name', 'content', 'created_at', 'replies']

    def get_replies(self, obj):
        if hasattr(obj, 'prefetched_replies'):
            replies = obj.prefetched_replies
        else:
            replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
    """C端文章列表卡片序列化器"""
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'cover',
            'tags', 'category',
            'like_count', 'comment_count', 'view_count',
            'author_name', 'status', 'published_at', 'updated_at'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """C端文章详情序列化器"""
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    comments = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'cover',
            'content_html', 'content_md',
            'tags', 'category',
            'like_count', 'comment_count', 'view_count',
            'author_name', 'status',
            'published_at', 'created_at', 'updated_at',
            'comments', 'user_has_liked'
        ]

    def get_comments(self, obj):
        top_comments = obj.comments.filter(parent__isnull=True).select_related('author')
        return CommentSerializer(top_comments, many=True).data

    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(article=obj, user=request.user).exists()
        return False


class CommentAdminSerializer(serializers.ModelSerializer):
    """S端评论管理序列化器"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'article_title', 'author', 'author_name',
                  'parent', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ArticleWriteSerializer(serializers.ModelSerializer):
    """S端文章写入序列化器（创建/更新）"""
    content_html = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Article
        fields = [
            'title', 'content_md', 'content_html',
            'summary', 'cover', 'status',
            'category', 'tags',
        ]

    def _make_slug(self, title):
        from django.utils.text import slugify
        from tools.generate_nums import generate_uuid7
        return slugify(title) or generate_uuid7()

    def _set_published_at(self, validated_data):
        from django.utils import timezone
        if validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()

    def create(self, validated_data):
        validated_data['slug'] = self._make_slug(validated_data['title'])
        self._set_published_at(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            validated_data['slug'] = self._make_slug(validated_data['title'])
        self._set_published_at(validated_data)
        return super().update(instance, validated_data)


class CommentCreateSerializer(serializers.ModelSerializer):
    """C端评论创建序列化器"""
    class Meta:
        model = Comment
        fields = ['id', 'article', 'parent', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
