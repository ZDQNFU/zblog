from django.db import models


class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键名')
    value = models.TextField(verbose_name='配置值')
    value_type = models.CharField(max_length=20, default='string', verbose_name='值类型')
    description = models.CharField(max_length=255, default='', blank=True, verbose_name='配置说明')
    is_encrypted = models.BooleanField(default=False, verbose_name='是否加密存储')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'system_config'
        ordering = ['-updated_at']
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['key'], name='idx_key'),
        ]

    def __str__(self):
        return self.key
