import os

from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import AIMessage, ToolMessage
from pyexpat.errors import messages

from chat_robot.tools import get_weather, search_func
from chat_robot.utils import get_llm_model, stream_chat_with_agent
from chat_robot.prompts import SYSTEM_PROMPT
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
# checkpointer = InMemorySaver()
import sqlite3

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# data 文件夹路径
data_dir = os.path.join(current_dir, "data")
# 确保 data 文件夹存在
os.makedirs(data_dir, exist_ok=True)
# 数据库文件完整路径
db_path = os.path.join(data_dir, "asuka_memory.db")

conn = sqlite3.connect(db_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)

agent = create_agent(
    model = get_llm_model(),
    system_prompt = SYSTEM_PROMPT,
    tools = [get_weather, search_func],
    middleware=[
        SummarizationMiddleware(
            model=get_llm_model(),
            trigger=("tokens", 4000),  # 达到4000 tokens时触发总结
            keep=("messages", 20),  # 保留最近20条消息
        )
    ],
    checkpointer=checkpointer,
)

# if __name__ == "__main__":
#     thread_id = "user_ZDQNFU"

#     while True:
#         user_input = input("\n你: ")
#         if user_input.lower() in ['quit', 'exit', '退出']:
#             print("明日香: 哼！走了就别回来！")
#             break
#         if not user_input.strip():
#             continue

#         print("明日香: ", end="", flush=True)
#         for token in stream_chat_with_agent(agent, user_input, thread_id):
#             print(token, end="", flush=True)
#         print()

