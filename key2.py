# -*- coding: utf-8 -*-
import time

from openai import OpenAI


# 使用环境变量管理 API Key
# client = OpenAI(api_key="sk-6f76cf8306a441259cfa462b22832765", base_url="https://api.deepseek.com")
client = OpenAI(api_key="9b53e79a8fef40f4b0410c2d1cab9c08.zlEwPycJW1B4hFhd", base_url="https://open.bigmodel.cn/api/paas/v4")

# 定义消息
messages = [
    {"role": "system", "content": "你是一个AI"},
    {
        "timestamp": "2025-04-18T11:11:07.518473",
        "role": "user",
        "content": "你好",
        "content_hash": -309889349970791610
    },
    {
        "timestamp": "2025-04-18T11:11:14.459305",
        "role": "assistant",
        "content": "你好！我是遗忘，一个致力于自我进化和任务自动化的AI助手。有什么可以帮你的吗？",
        "content_hash": 3607682978751466858
    },
    {
        "timestamp": "2025-04-18T11:11:23.790798",
        "role": "user",
        "content": "随便放一首歌",
        "content_hash": 7822299132786278376
    },
    {
        "timestamp": "2025-04-18T11:11:29.501507",
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": "call_0_50222fdf-374b-4ef1-85c5-2f5d4c6e987b",
                "function": {
                    "name": "play_music",
                    "arguments":"file:music"

                },
                "type": "function",
                "index": 0
            }
        ]
    },
    {
        "timestamp": "2025-04-18T11:11:29.502509",
        "role": "tool",
        "tool_call_id": "call_0_50222fdf-374b-4ef1-85c5-2f5d4c6e987b",
        "content": "音乐播放成功: 播放中"
    },
    {
        "timestamp": "2025-04-18T11:11:65.459305",
        "role": "assistant",
        "content": "音乐已经播放，成功，现在正在播放中。享受音乐吧！如果你有其他需求或者想听特定的歌曲，随时告诉我。",
        "content_hash": 3607682978751466858
    }
]

messages2 = [
    {"role": "system", "content": "你是一个超级AI"},
    *[
        # 基础结构
        {"role": msg["role"], "content": msg.get("content", "")}
        # 处理 assistant 的工具调用
        | ({"tool_calls": msg["tool_calls"]} if msg.get("tool_calls") else {})
        # 处理 tool 消息
        | ({"tool_call_id": msg["tool_call_id"]} if msg.get("tool_call_id") else {})
        for msg in messages  # 跳过原始系统消息
    ]
]

print(messages2)

# 流式返回
response = client.chat.completions.create(
    model="glm-4-plus",
    messages=messages,
    stream=True,
    max_tokens=1000,
    tools=[
            {
                "type": "function",
                "function": {
                    "name": "play_music",
                    "description": "播放音乐",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string", "description": "音乐路径"},
                            "volume": {"type": "number", "description": "音量，范围 0.0-1.0"}
                        },
                        "required": ["file", "volume"]
                    }
                }
            },
    {
        "type": "function",
        "function": {
            "name": "speak",
            "description": "说话功能",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "说话的内容"},
                    "voice_key": {"type": "string", "description": "语音类型，如 'cn_female', 'cn_male', 'en_female', 'en_male'"},
                    "rate": {"type": "number", "description": "语速，默认 150"},
                    "volume": {"type": "number", "description": "音量，范围 0.0-1.0，默认 1.0"},
                    "pitch": {"type": "number", "description": "音高倍率，默认 1.0"}
                },
                "required": ["text", "voice_key"]
            }
        }
    }
        ],
        tool_choice="auto"
)

if __name__ == '__main__':
    # 实时打印进度
    print("文章生成中...\n")
    for chunk in response:
        # 直接访问 delta.content 属性
        content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, "content") else ""

        if content:
            print(content, end="", flush=True)
