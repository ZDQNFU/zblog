from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tools.cache_utils import cache_result, invalidate
from message.models import Message, MessageLike
from message.serializers import MessageSerializer, MessageWriteSerializer


class MessageListView(generics.ListAPIView):
    """C端：留言列表（不隐藏，按时间倒序，不分页）"""
    serializer_class = MessageSerializer
    pagination_class = None

    def get_queryset(self):
        return Message.objects.filter(is_hidden=0).order_by('-created_at')

    @cache_result('c:messages', timeout=30)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MessageCreateView(generics.CreateAPIView):
    """C端：创建留言（登录绑定用户，匿名user为空）"""
    serializer_class = MessageWriteSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
        invalidate('c:messages')


class MessageLikeToggleView(APIView):
    """C端：留言点赞/取消点赞（需登录）"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            message = Message.objects.get(pk=pk, is_hidden=0)
        except Message.DoesNotExist:
            return Response({'detail': '留言不存在'}, status=status.HTTP_404_NOT_FOUND)
        try:
            MessageLike.objects.create(message=message, user=request.user)
            message.like_count = message.likes.count()
            message.save(update_fields=['like_count'])
            return Response({'liked': True, 'like_count': message.like_count})
        except IntegrityError:
            return Response({'detail': '已经点过赞了'}, status=status.HTTP_409_CONFLICT)

    def delete(self, request, pk):
        try:
            message = Message.objects.get(pk=pk, is_hidden=0)
        except Message.DoesNotExist:
            return Response({'detail': '留言不存在'}, status=status.HTTP_404_NOT_FOUND)
        deleted, _ = MessageLike.objects.filter(message=message, user=request.user).delete()
        if deleted:
            message.like_count = message.likes.count()
            message.save(update_fields=['like_count'])
            return Response({'liked': False, 'like_count': message.like_count})
        return Response({'detail': '尚未点赞'}, status=status.HTTP_404_NOT_FOUND)
