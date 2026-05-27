from django.db import models
from django.contrib.auth import get_user_model
from tools.generate_nums import generate_uuid7

User = get_user_model()


class ResourceLink(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=32,
        default=generate_uuid7,
        editable=False,
        verbose_name='ID'
    )
    name = models.CharField('名称', max_length=200)
    url = models.URLField('链接', max_length=2000)
    image_url = models.URLField('图片', blank=True)
    color = models.CharField(
        '主题色',
        max_length=7,
        default='#3b82f6',
        help_text='十六进制颜色码，如 #ff0000'
    )
    description = models.TextField('简介', blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_links',
        verbose_name='创建人'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_links',
        verbose_name='最后修改人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后修改时间', auto_now=True)

    class Meta:
        db_table = 'link_link'
        verbose_name = '资源链接'
        verbose_name_plural = '资源链接'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
