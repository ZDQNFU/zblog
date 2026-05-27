from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response


class LoginRateThrottle:
    """登录频率限制：每超过5次失败，等待时间翻倍（1分钟、2分钟、4分钟...）"""

    def __init__(self):
        self.key_prefix = 'login_attempts'
        self.threshold = 5  # 第5次开始限制

    def _get_cache_key(self, username):
        return f'{self.key_prefix}:{username}'

    def get_attempts(self, username):
        if not username:
            return 0, 0
        data = cache.get(self._get_cache_key(username))
        if data is None:
            return 0, 0
        return data.get('count', 0), data.get('locked_until', 0)

    def record_failure(self, username):
        if not username:
            return
        key = self._get_cache_key(username)
        data = cache.get(key) or {'count': 0, 'locked_until': 0}
        data['count'] += 1

        if data['count'] >= self.threshold:
            excess = data['count'] - self.threshold
            wait_seconds = 60 * (2 ** excess)  # 60, 120, 240, 480...
            import time
            data['locked_until'] = int(time.time()) + wait_seconds

        # 存储24小时
        cache.set(key, data, timeout=86400)

    def reset(self, username):
        if username:
            cache.delete(self._get_cache_key(username))

    def is_locked(self, username):
        if not username:
            return False, 0
        _, locked_until = self.get_attempts(username)
        import time
        now = int(time.time())
        if locked_until > now:
            return True, locked_until - now
        return False, 0
