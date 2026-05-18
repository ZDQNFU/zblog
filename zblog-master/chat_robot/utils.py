from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

#加载env环境变量
load_dotenv()

def get_llm_model():
    model_map = {
        'deepseek' : ChatOpenAI(
            model = os.getenv('DEEPSEEK_LLM_MODEL'),
            api_key = os.getenv('DEEPSEEK_API_KEY'),
            base_url = os.getenv('DEEPSEEK_BASE_URL'),
            temperature = os.getenv('TEMPERATURE'),
            max_tokens = int(os.getenv('MAX_TOKENS')),
            extra_body={"thinking": {"type": "disabled"}}
        )
    }
    model_type = os.getenv('LLM_MODEL')
    return model_map.get(model_type)


def chat_with_agent(agent, user_input, thread_id="default-thread"):
    """简化的聊天接口"""
    # 统一处理输入格式
    if isinstance(user_input, str):
        messages = [HumanMessage(content=user_input)]
    else:
        messages = user_input

    config = {"configurable": {"thread_id": thread_id}}
    return agent.invoke({"messages": messages}, config=config)


def stream_chat_with_agent(agent, user_input, thread_id="default-thread"):
    """
    流式聊天
    """
    config = {"configurable": {"thread_id": thread_id}}

    for chunk in agent.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages"
    ):
        if isinstance(chunk, tuple) and len(chunk) == 2:
            message, metadata = chunk
            if hasattr(message, 'content') and message.content:
                if isinstance(message.content, str):
                    yield message.content
                elif isinstance(message.content, list):
                    for item in message.content:
                        if isinstance(item, dict) and 'text' in item:
                            yield item['text']
                        elif isinstance(item, str):
                            yield item

def extract_ai_response(result):
    """从结果中提取 AI 的回复文本"""
    messages = result.get("messages", [])
    ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]
    return ai_messages[-1] if ai_messages else None