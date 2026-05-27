from rest_framework import serializers
from .models import Message, MessageLike


class MessageSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'user_name', 'content', 'like_count',
                  'is_hidden', 'created_at', 'user_has_liked']

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.username
        return '游客'

    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return MessageLike.objects.filter(
                message=obj, user=request.user
            ).exists()
        return False


class MessageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']


class MessageAdminSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'user_name', 'content', 'like_count',
                  'is_hidden', 'created_at']
        read_only_fields = ['id', 'created_at', 'like_count']
