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

@wrap_tool_call
def handle_tool_errors(request, handler):
    """使用自定义消息处理工具执行错误。"""
    try:
        return handler(request)
    except Exception as e:
        # 向模型返回自定义错误消息
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
    # 获取定位：使用IP地址获取大致位置
    g = geocoder.ip('me')
    if not g.ok or not g.latlng:
        return "抱歉，无法获取当前位置信息，请检查网络连接。"

    latitude, longitude = g.latlng
    city = g.city or "您所在的区域"

    # 查询天气：使用 Open-Meteo 免费天气API
    try:
        openmeteo = openmeteo_requests.Client()
        url = "https://api.open-meteo.com/v1/forecast"

        # 获取今天的日期范围
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

        # 提取天气数据
        daily = response.Daily()
        if daily.VariablesLength() == 0:
            return f"已定位到 {city}（坐标 {latitude:.2f}, {longitude:.2f}），但暂时获取不到天气数据。"

        temp_max = daily.Variables(0).ValuesAsNumpy()[0]
        temp_min = daily.Variables(1).ValuesAsNumpy()[0]
        weather_code = int(daily.Variables(2).ValuesAsNumpy()[0])

        # 简易天气代码转文字
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

        # 直接返回原始搜索结果，不做任何总结
        return query_result

    except Exception as e:
        return f"搜索错误: {str(e)}"