from rest_framework import serializers
from tracking.models import Visitor, Pageview


class PageviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pageview
        fields = ['id', 'url', 'referer', 'query_string', 'method', 'view_time']


class VisitorSerializer(serializers.ModelSerializer):
    pageviews = PageviewSerializer(many=True, read_only=True)
    username = serializers.SerializerMethodField()

    class Meta:
        model = Visitor
        fields = [
            'session_key', 'user', 'username', 'ip_address', 'user_agent',
            'start_time', 'expiry_age', 'expiry_time', 'time_on_site',
            'end_time', 'pageviews',
        ]

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return f'游客{obj.ip_address}'
