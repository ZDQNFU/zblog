import logging
import requests
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tracking.models import Visitor, Pageview

from user.permissions import IsSuperAdmin
from .serializers import VisitorSerializer, PageviewSerializer

logger = logging.getLogger(__name__)


class VisitorListView(generics.ListAPIView):
    """访问日志列表（支持 ?search=IP/用户名 搜索）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = VisitorSerializer

    def get_queryset(self):
        qs = Visitor.objects.prefetch_related('pageviews').all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(ip_address__icontains=search) |
                Q(user__username__icontains=search)
            )
        return qs


class VisitorDetailView(generics.RetrieveDestroyAPIView):
    """访问日志详情 / 删除"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = VisitorSerializer
    lookup_field = 'session_key'

    def get_queryset(self):
        return Visitor.objects.prefetch_related('pageviews').all()


class VisitorDeleteView(APIView):
    """批量删除访问日志"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        keys = request.data.get('session_keys', [])
        if not keys:
            return Response({'detail': '请提供要删除的 session_key 列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = Visitor.objects.filter(session_key__in=keys).delete()
        return Response({'detail': f'已删除 {deleted} 条记录'})


class VisitorGeoView(APIView):
    """返回访问者IP地理分布数据（用于地图展示）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        from django.core.cache import cache

        visitors = Visitor.objects.values('ip_address').distinct()[:200]
        geo_data = []

        for v in visitors:
            ip = v['ip_address']
            if not ip or ip.startswith('127.') or ip.startswith('192.168.') or ip.startswith('10.'):
                continue

            cache_key = f'ip_geo_v2_{ip}'
            cached = cache.get(cache_key)
            if cached is not None:
                if cached.get('lat'):
                    geo_data.append(cached)
                continue

            try:
                resp = requests.get(
                    f'http://ip-api.com/json/{ip}',
                    params={'lang': 'zh-CN'},
                    timeout=5,
                )
                data = resp.json()
                if data.get('status') == 'success':
                    entry = {
                        'ip': ip,
                        'lat': data.get('lat'),
                        'lon': data.get('lon'),
                        'city': data.get('city', ''),
                        'country': data.get('country', ''),
                    }
                    cache.set(cache_key, entry, 86400)
                    geo_data.append(entry)
                else:
                    cache.set(cache_key, {}, 3600)
            except Exception as e:
                logger.warning(f'Geo lookup failed for IP {ip}: {e}')
                cache.set(cache_key, {}, 600)

        return Response({'points': geo_data})
