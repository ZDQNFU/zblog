from uuid6 import uuid7

def generate_uuid7():
    """生成 UUID v7（时间有序），返回不含连字符的 hex 字符串"""
    return uuid7().hex