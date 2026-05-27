import random
import string
from django.core.cache import cache


def generate_captcha():
    """生成数学算式验证码，返回 (算式字符串, 答案, captcha_key)"""
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    ops = [('+', a + b), ('-', a - b), ('×', a * b)]
    op, answer = random.choice(ops)
    # 减法避免负数
    if op == '-' and a < b:
        a, b = b, a
        answer = a - b
    expr = f'{a} {op} {b} = ?'
    captcha_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    cache.set(f'captcha:{captcha_key}', str(answer), timeout=300)
    return expr, captcha_key


def verify_captcha(captcha_key, answer):
    cached = cache.get(f'captcha:{captcha_key}')
    if cached is None:
        return False
    cache.delete(f'captcha:{captcha_key}')
    return cached == str(answer).strip()
