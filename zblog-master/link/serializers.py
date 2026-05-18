from rest_framework import serializers
from .models import ResourceLink


class ResourceLinkSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ResourceLink
        fields = [
            'id', 'name', 'url', 'image_url', 'color', 'description',
            'created_by', 'created_by_name', 'updated_by',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']
