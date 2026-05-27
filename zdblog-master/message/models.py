from django.db import models
from django.contrib.auth import get_user_model
from tools.generate_nums import generate_uuid7

User = get_user_model()


class Message(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=32,
        default=generate_uuid7,
        editable=False,
        verbose_name='ID'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name='用户'
    )
    content = models.CharField('留言内容', max_length=100)
    like_count = models.IntegerField('点赞数', default=0)
    is_hidden = models.IntegerField('是否隐藏', default=0)  # 1隐藏 0不隐藏
    created_at = models.DateTimeField('留言时间', auto_now_add=True)

    class Meta:
        db_table = 'message'
        verbose_name = '留言'
        verbose_name_plural = '留言'
        ordering = ['-created_at']

    def __str__(self):
        preview = self.content[:20] + '...' if len(self.content) > 20 else self.content
        return f'{preview}'


class MessageLike(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='留言'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_likes',
        verbose_name='用户'
    )
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)

    class Meta:
        db_table = 'message_like'
        verbose_name = '留言点赞'
        verbose_name_plural = '留言点赞'
        constraints = [
            models.UniqueConstraint(
                fields=['message', 'user'],
                name='unique_message_user_like'
            )
        ]

    def __str__(self):
        return f'{self.user.username} 点赞了 {self.message}'
