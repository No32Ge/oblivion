# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import threading

# 创建线程局部存储容器
thread_local = threading.local()

def get_client():
    # 每个线程独立创建客户端实例
    if not hasattr(thread_local, "client"):
        thread_local.client = OpenAI(
            api_key="sk-497f472f192946a695a71e8b0680e18f",
            base_url="https://api.deepseek.com"
        )
    return thread_local.client

def call_api():
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "你好"}],
            stream=False,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "play_music",
                        "description": "播放音乐文件",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file": {"type": "string", "description": "音乐文件路径"},
                                "volume": {"type": "number", "description": "音量，范围 0.0-1.0"}
                            },
                            "required": ["file", "volume"]
                        }
                    }
                }
            ]
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"API调用失败: {str(e)}")

if __name__ == '__main__':
    # 建议根据API速率限制调整max_workers
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(call_api) for _ in range(3)]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"线程执行异常: {str(e)}")