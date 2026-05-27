from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import ResourceLink
from ..serializers import ResourceLinkSerializer


class SResourceLinkListCreateView(generics.ListCreateAPIView):
    """S端：资源链接列表 & 创建"""
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'description', 'created_by__username']
    serializer_class = ResourceLinkSerializer

    def get_queryset(self):
        return ResourceLink.objects.select_related('created_by').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SResourceLinkRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """S端：资源链接详情 & 更新 & 删除"""
    permission_classes = [IsAuthenticated]
    serializer_class = ResourceLinkSerializer

    def get_queryset(self):
        return ResourceLink.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
