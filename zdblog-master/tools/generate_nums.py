from uuid6 import uuid7
from django.core.signing import dumps, loads


def generate_uuid7():
    """生成 UUID v7（时间有序），返回不含连字符的 hex 字符串"""
    return uuid7().hex


def encrypt_value(value):
    """使用 Django 内置签名加密字符串"""
    return dumps(value)


def decrypt_value(value):
    """解密 Django 内置签名加密的字符串，失败时返回原文"""
    try:
        return loads(value)
    except Exception:
        return value
