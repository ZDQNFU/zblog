from rest_framework import generics
from tools.cache_utils import cache_result
from ..models import ResourceLink
from ..serializers import ResourceLinkSerializer


class ResourceLinkListView(generics.ListAPIView):
    """C端：资源链接列表（公开）"""
    serializer_class = ResourceLinkSerializer

    def get_queryset(self):
        return ResourceLink.objects.order_by('-created_at')

    @cache_result('c:links', timeout=1800)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
