from rest_framework import generics
from ..models import ResourceLink
from ..serializers import ResourceLinkSerializer


class ResourceLinkListView(generics.ListAPIView):
    """C端：资源链接列表（公开）"""
    serializer_class = ResourceLinkSerializer

    def get_queryset(self):
        return ResourceLink.objects.order_by('-created_at')
