from django.contrib import admin
from .models import ResourceLink


@admin.register(ResourceLink)
class ResourceLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'color', 'created_by', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
