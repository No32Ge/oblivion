# -*- coding: utf-8 -*-
from openai import OpenAI

# 初始化 API 客户端（放外面，避免每次都重连）
client = OpenAI(
    api_key="sk-71bbd7d4dce44c84a00be724db9dbf8f",
    base_url="https://api.deepseek.com"
)

def generate_article(prompt):
    """
    根据给定 prompt，实时流式生成文章内容。
    返回值：None（直接打印）
    """
    messages = [
        {"role": "system", "content": "你的职责是完成我的要求"},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True
    )

    for chunk in response:
        content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, "content") else ""
        if content:
            print(content, end="", flush=True)
