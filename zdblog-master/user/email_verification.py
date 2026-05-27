import random

from django.core.cache import cache
from django.core.mail import send_mail


def generate_verification_code(email):
    code = ''.join(random.choices('0123456789', k=6))
    cache.set(f'email_verify:{email}', code, timeout=300)
    send_mail(
        subject='ZDBlog 邮箱验证码',
        message=f'您的验证码是：{code}，5分钟内有效。',
        from_email=None,
        recipient_list=[email],
    )
    return code


def verify_code(email, code):
    cached = cache.get(f'email_verify:{email}')
    if cached is None:
        return False
    if cached != str(code).strip():
        return False
    cache.delete(f'email_verify:{email}')
    return True
