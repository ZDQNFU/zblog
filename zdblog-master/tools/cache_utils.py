"""
Redis 缓存工具 — 基于 django-redis 的缓存装饰器和失效辅助函数。
"""
from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response


def cache_result(key: str, timeout: int = 300):
    """
    装饰器：缓存 DRF APIView 方法的 Response 返回值。

    DRF Response 在渲染前无法序列化，因此只缓存 .data 和 status_code，
    命中时重建 Response 对象。

    用法:
        @cache_result('dashboard:stats', timeout=300)
        def get(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            cached = cache.get(key)
            if cached is not None:
                return Response(data=cached['data'], status=cached.get('status', 200))
            response = func(view_instance, request, *args, **kwargs)
            cache.set(key, {'data': response.data, 'status': response.status_code}, timeout)
            return response
        return wrapper
    return decorator


def cached_or_fetch(key: str, timeout: int, fetch_func):
    """从缓存读取，未命中则调用 fetch_func 并写入缓存。"""
    result = cache.get(key)
    if result is not None:
        return result
    result = fetch_func()
    cache.set(key, result, timeout)
    return result


def invalidate(*keys: str):
    """批量删除缓存键。"""
    for key in keys:
        cache.delete(key)


def invalidate_pattern(pattern: str):
    """按通配符模式删除缓存（依赖 django-redis 扩展）。"""
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)
    else:
        # 回退：尝试用 keys + delete_many
        if hasattr(cache, 'keys'):
            matching = cache.keys(pattern)
            if matching:
                cache.delete_many(matching)
