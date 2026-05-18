from django.db import models
from django.contrib.auth.models import User
from tools.generate_nums import generate_uuid7


class ChatMessage(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=generate_uuid7)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10)  # 'human' or 'ai'
    content = models.TextField()
    token_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'[{self.role}] {self.user.username} @ {self.created_at}'
