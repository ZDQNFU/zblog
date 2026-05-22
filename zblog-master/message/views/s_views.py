from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from message.models import Message
from message.serializers import MessageAdminSerializer, MessageWriteSerializer


class SMessageListCreateView(generics.ListCreateAPIView):
    """S端：留言列表 & 创建"""
    permission_classes = [IsAuthenticated]
    search_fields = ['content', 'user__username']

    def get_queryset(self):
        qs = Message.objects.select_related('user').order_by('-created_at')
        after = self.request.query_params.get('created_at_after')
        before = self.request.query_params.get('created_at_before')
        if after:
            qs = qs.filter(created_at__gte=after)
        if before:
            qs = qs.filter(created_at__lte=before)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MessageAdminSerializer
        return MessageWriteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SMessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """S端：留言详情 & 更新 & 删除"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    queryset = Message.objects.select_related('user')

    def get_serializer_class(self):
        return MessageAdminSerializer
