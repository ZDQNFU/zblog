import json
import shutil
import subprocess
from datetime import datetime

from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
import geocoder
import openmeteo_requests
from langchain_core.messages import ToolMessage
import os

import requests

# ── 情感分析：中文情感词典 ──

POSITIVE_WORDS = {
    "开心", "高兴", "快乐", "兴奋", "激动", "满足", "幸福", "欣慰", "惊喜",
    "喜欢", "爱", "热爱", "好评", "太棒", "优秀", "厉害", "牛", "强",
    "感谢", "谢谢", "多谢", "感恩", "感动", "温暖", "贴心", "赞", "好耶",
    "哈哈", "嘿嘿", "嘻嘻", "呵呵", "真好", "好好", "太强了", "漂亮",
    "舒服", "爽", "过瘾", "完美", "精彩", "出色", "帅", "酷", "给力",
    "不错", "还行", "挺好的", "还好", "可以", "值得", "支持", "加油",
    "真棒", "nice", "good", "wow", "cool", "amazing", "love",
}

NEGATIVE_WORDS = {
    "难过", "伤心", "痛苦", "悲伤", "郁闷", "压抑", "焦虑", "烦躁", "生气",
    "愤怒", "讨厌", "恨", "烦", "累", "疲惫", "无聊", "孤独", "寂寞",
    "失望", "绝望", "崩溃", "受不了", "糟糕", "差劲", "恶心", "垃圾",
    "想哭", "哭了", "呜呜", "唉", "烦死了", "好累", "太难", "好难",
    "别烦我", "走开", "滚", "闭嘴", "不要", "不好", "不行", "难受",
    "错了", "错误", "失败", "输了", "没了", "没救了", "完蛋", "死",
    "不好玩", "没用", "废物", "气死", "恼火", "暴躁", "怒了",
    "bad", "sad", "hate", "angry", "terrible", "awful",
}

INTENSIFIERS = {"很", "非常", "特别", "超级", "太", "好", "真的", "极度", "极其", "贼", "巨"}

NEGATIONS = {"不", "没", "没有", "别", "不要", "并不", "无", "非", "莫"}

EMOTION_CATEGORIES = {
    "喜悦": {"开心", "高兴", "快乐", "兴奋", "激动", "满足", "幸福", "欣慰", "惊喜",
             "哈哈", "嘿嘿", "嘻嘻", "呵呵", "好耶", "爽", "过瘾", "太棒"},
    "愤怒": {"生气", "愤怒", "气死", "恼火", "暴躁", "怒了", "讨厌", "恨", "烦死了", "滚"},
    "悲伤": {"难过", "伤心", "痛苦", "悲伤", "想哭", "哭了", "呜呜", "绝望", "崩溃"},
    "焦虑": {"焦虑", "烦躁", "压抑", "紧张", "担心", "害怕", "怕"},
    "疲惫": {"累", "疲惫", "困", "好累", "无聊", "倦了", "乏了"},
    "喜爱": {"喜欢", "爱", "热爱", "好评", "赞", "感谢", "谢谢", "感动", "温暖", "贴心", "love"},
    "失望": {"失望", "糟糕", "差劲", "垃圾", "无语", "算了", "没救了", "完蛋"},
    "孤独": {"孤独", "寂寞", "一个人", "没人", "别烦我", "走开"},
}


def _analyze_sentiment(text: str) -> str:
    """基于词典的中文情感分析，返回结构化的情感数据供模型内部使用。"""
    text_lower = text.lower()

    pos_count = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg_count = sum(1 for w in NEGATIVE_WORDS if w in text_lower)

    has_intensifier = any(w in text_lower for w in INTENSIFIERS)
    has_negation = any(w in text_lower for w in NEGATIONS)

    emotions = []
    for category, keywords in EMOTION_CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            emotions.append(category)

    if neg_count > pos_count and has_intensifier:
        polarity = "强烈负面"
    elif neg_count > pos_count:
        polarity = "负面"
    elif pos_count > neg_count and has_intensifier:
        polarity = "强烈正面"
    elif pos_count > neg_count:
        polarity = "正面"
    else:
        polarity = "中性"

    result = f"情感倾向：{polarity}（正面词{pos_count}个，负面词{neg_count}个）"
    if emotions:
        result += f"\n检测到的情绪：{'、'.join(emotions)}"
    if has_negation:
        result += "\n注意：用户使用了否定词，语义可能反转，请结合上下文判断。"

    style_tips = {
        "强烈负面": "用户情绪激动，明日香应先收起嘲讽，用傲娇的方式表达关心，切忌火上浇油。",
        "负面": "用户心情不好，明日香嘴上嫌弃但要偷偷安慰，可以转移话题或提供帮助。",
        "中性": "用户状态正常，明日香保持一贯的骄傲毒舌风格即可。",
        "正面": "用户心情好，明日香可以更放松地互动，甚至一起快乐吐槽。",
        "强烈正面": "用户非常开心，明日香可以跟着high，但还是要保持傲娇人设不崩。",
    }
    result += f"\n回话建议：{style_tips.get(polarity, style_tips['中性'])}"

    return result


@wrap_tool_call
def handle_tool_errors(request, handler):
    """使用自定义消息处理工具执行错误。"""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"工具错误：请检查您的输入并重试。({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


@tool
def get_weather():
    """
    当用户询问今天天气、气温、是否下雨、是否需要带伞等天气相关问题时，调用此工具。
    自动获取当前设备位置，返回当天天气状况、最高温度和最低温度。
    """
    g = geocoder.ip('me')
    if not g.ok or not g.latlng:
        return "抱歉，无法获取当前位置信息，请检查网络连接。"

    latitude, longitude = g.latlng
    city = g.city or "您所在的区域"

    try:
        openmeteo = openmeteo_requests.Client()
        url = "https://api.open-meteo.com/v1/forecast"
        today = datetime.now().strftime("%Y-%m-%d")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["temperature_2m_max", "temperature_2m_min", "weathercode"],
            "timezone": "auto",
            "start_date": today,
            "end_date": today
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        daily = response.Daily()
        if daily.VariablesLength() == 0:
            return f"已定位到 {city}（坐标 {latitude:.2f}, {longitude:.2f}），但暂时获取不到天气数据。"

        temp_max = daily.Variables(0).ValuesAsNumpy()[0]
        temp_min = daily.Variables(1).ValuesAsNumpy()[0]
        weather_code = int(daily.Variables(2).ValuesAsNumpy()[0])

        weather_map = {
            0: "晴天", 1: "大部晴朗", 2: "多云", 3: "阴天",
            45: "有雾", 51: "小雨", 61: "中雨", 71: "小雪", 80: "阵雨"
        }
        weather_desc = weather_map.get(weather_code, f"天气代码 {weather_code}")

        return f"{city}今天天气：{weather_desc}，最高温 {temp_max:.1f}°C，最低温 {temp_min:.1f}°C。"

    except Exception as e:
        return f"已定位到 {city}，但天气查询失败：{str(e)}"


@tool
def search_func(query):
    """
    当用户需要查询实时信息、最新新闻、网络搜索、查找资料、了解时事时使用此工具。

    适用场景：
    - 用户问"今天/现在/最新"开头的问题（如：今天天气、最新新闻、现在发生的事）
    - 用户要求搜索、查找、查一下某事物
    - 用户想知道某个具体事实、数据、事件（如：某地旅游攻略、某产品价格、某人物信息）
    - 用户的提问超出了你已有的知识范围
    - 用户问的是你训练数据截止日期之后的事情

    输入：用户想搜索的关键词或问题
    返回：相关搜索结果的标题、摘要和链接
    """
    search_url = os.getenv('SEARCH_URL')
    search_api_key = os.getenv('SEARCH_API_KEY')

    payload = {
        "query": query,
        "summary": True,
        "count": 10
    }
    headers = {
        'Authorization': 'Bearer ' + search_api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(search_url, headers=headers, json=payload, timeout=10)
        search_result = response.json()

        query_result = ""
        if search_result.get('code') == 200:
            data = search_result.get('data', {})
            if data:
                web_pages = data.get('webPages', {})
                if web_pages and 'value' in web_pages:
                    for item in web_pages['value']:
                        query_result += f"标题：{item.get('name', '')}\n"
                        query_result += f"摘要：{item.get('snippet', '')}\n"
                        query_result += f"链接：{item.get('url', '')}\n\n"

        if not query_result.strip():
            return "未找到相关信息"

        return query_result

    except Exception as e:
        return f"搜索错误: {str(e)}"


@tool
def analyze_sentiment(text: str) -> str:
    """
    分析用户输入文本的情感，返回情感分析数据。

    **重要：此工具的返回结果是给你（明日香）内部参考用的，绝不要在回复中直接说出分析结果！**
    例如绝对不能说"检测到你是负面情绪"、"你的情感倾向是..."、"根据情感分析..."等话语。

    正确的用法：
    - 先调用此工具分析用户情感
    - 根据分析结果中的"回话建议"调整你的语气和回应策略
    - 用明日香的方式自然回应，让用户感受到你的关心（当然要嘴硬）

    调用时机：每次用户说话时都应该调用此工具，以便根据用户情绪调整回应方式。

    输入：用户的原文
    返回：情感分析结果（包含情感倾向、检测到的情绪、回话建议）
    """
    return _analyze_sentiment(text)
