from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import time

# DeepSeek 客户端
client = OpenAI(
    api_key="sk-71bbd7d4dce44c84a00be724db9dbf8f",
    base_url="https://api.deepseek.com"
)

def call_deepseek(_):
    start = time.time()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "你好，简单回复一下。"}],
        temperature=0.7
    )
    duration = time.time() - start
    print(f"✅ 完成一个请求，耗时 {duration:.2f} 秒")
    return response.choices[0].message.content

start_time = time.time()

# 并发数量
num_threads = 5

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    results = list(executor.map(call_deepseek, range(num_threads)))

total_time = time.time() - start_time

print(f"\n🌟 共 {num_threads} 个请求，总耗时 {total_time:.2f} 秒")
