from django.db import models
from django.contrib.auth import get_user_model
from tools.generate_nums import generate_uuid7

User = get_user_model()


class Category(models.Model):
    # ID
    id = models.CharField(
        primary_key=True,
        max_length=32,
        default=generate_uuid7,
        editable=False,
        verbose_name='ID'
    )
    # 分类名
    name = models.CharField('分类名', max_length=50, unique=True)

    # 创建与修改人
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_categories',
        verbose_name='创建人'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_categories',
        verbose_name='最后修改人'
    )

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后修改时间', auto_now=True)

    class Meta:
        db_table = 'article_category'
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['-created_at']  # 按创建时间倒序

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=32,
        default=generate_uuid7,
        editable=False,
        verbose_name='ID'
    )
    name = models.CharField('标签名', max_length=50, unique=True)
    color = models.CharField(
        '标签颜色',
        max_length=7,
        default='#3b82f6',          # 默认蓝色
        help_text='十六进制颜色码，如 #ff0000'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tags',
        verbose_name='创建人'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_tags',
        verbose_name='最后修改人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后修改时间', auto_now=True)

    class Meta:
        # db_table: 指定数据库中的表名
        db_table = 'article_tag'
        # verbose_name: 在 Django Admin 或表单中显示的单数名称
        verbose_name = '标签'
        # verbose_name_plural: 在 Django Admin 或表单中显示的复数名称
        verbose_name_plural = '标签'
        # ordering: 默认查询排序规则
        ordering = ['-created_at']

    def __str__(self):
        """
        定义对象的字符串表示形式。
        当打印 Tag 实例或在 Django Admin 列表中显示时，将返回标签的名称。
        """
        return self.name


class Article(models.Model):

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_PRIVATE = 'private'

    STATUS_CHOICES = [
        (STATUS_DRAFT, '草稿'),
        (STATUS_PUBLISHED, '已发布'),
        (STATUS_PRIVATE, '私密'),
    ]

    id = models.CharField(
        primary_key=True,
        max_length=32,
        default=generate_uuid7,
        editable=False,
        verbose_name='ID'
    )

    title = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    summary = models.CharField(max_length=300, blank=True)

    content_md = models.TextField()

    content_html = models.TextField(blank=True)

    cover = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )

    view_count = models.IntegerField(default=0)

    like_count = models.IntegerField(default=0)

    comment_count = models.IntegerField(default=0)

    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    tags = models.ManyToManyField(Tag, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # db_table: 指定数据库中的表名
        db_table = 'article'
        # verbose_name: 在 Django Admin 或表单中显示的单数名称
        verbose_name = '文章'
        # verbose_name_plural: 在 Django Admin 或表单中显示的复数名称
        verbose_name_plural = '文章'
        # ordering: 默认查询排序规则
        ordering = ['-created_at']

    def __str__(self):
        """
        定义对象的字符串表示形式。
        当打印 Article 模型实例时，将返回文章的标题。
        """
        return self.title


class Comment(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=32,
        default=generate_uuid7,
        editable=False,
        verbose_name='ID'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属文章'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments',
        verbose_name='评论者'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='父评论'
    )
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('评论时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后修改时间', auto_now=True)

    class Meta:
        db_table = 'article_comment'
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} 评论了 {self.article}'


class Like(models.Model):
    """文章点赞（用户+文章唯一，可取消）"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='文章'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='用户'
    )
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)

    class Meta:
        db_table = 'article_like'
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        constraints = [
            models.UniqueConstraint(
                fields=['article', 'user'],
                name='unique_article_user_like'
            )
        ]

    def __str__(self):
        return f'{self.user} 点赞了 {self.article}'
