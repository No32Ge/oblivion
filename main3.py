# -*- coding: utf-8 -*-
from openai import OpenAI
from multiprocessing import Process
import os

# 配置 OpenAI 客户端
client = OpenAI(api_key="sk-71bbd7d4dce44c84a00be724db9dbf8f", base_url="https://api.deepseek.com")

# 定义一个函数，接收单个 prompt 处理
def generate_article(prompt, process_name):
    messages = [
        {"role": "system", "content": "你的职责是完成我的要求"},
        {"role": "user", "content": prompt},
    ]

    print(f"\n[{process_name}] 文章生成中... (PID: {os.getpid()})\n")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True
    )

    for chunk in response:
        content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, "content") else ""
        if content:
            print(f"[{process_name}] {content}", end="", flush=True)

    print(f"\n[{process_name}] 完成！")

# 多进程任务管理函数
def run_multiprocess(prompts):
    processes = []
    for i, prompt in enumerate(prompts):
        process_name = f"进程{i+1}"
        p = Process(target=generate_article, args=(prompt, process_name))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()  # 等待所有进程完成

# 示例：多个 prompt 列表
prompts = [
    "请翻译并生成格式：One day I saw a bird.",
    "请翻译并生成格式：It started raining heavily.",
    "请翻译并生成格式：We found a hidden cave."
]

if __name__ == '__main__':
    run_multiprocess(prompts)
