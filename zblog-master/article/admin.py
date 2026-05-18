from django.contrib import admin

from article.models import Article, Category, Tag, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['-created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_by', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'view_count', 'like_count', 'comment_count', 'published_at', 'created_at']
    list_filter = ['status', 'category', 'tags']
    search_fields = ['title', 'summary']
    ordering = ['-created_at']
    filter_horizontal = ['tags']
    readonly_fields = ['slug', 'view_count', 'like_count', 'comment_count']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'author', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']
