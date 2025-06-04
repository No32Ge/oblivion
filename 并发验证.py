# -*- coding: utf-8 -*-
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from openai import RateLimitError

# 配置参数
THREAD_NUM = 3  # 并发线程数
REQUEST_TIMEOUT = 30  # 单次请求超时时间

# 线程安全锁
print_lock = threading.Lock()
stats = {
    "success": 0,
    "rate_limited": 0,
    "errors": 0,
    "start_time": None,
    "end_time": None
}


def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


class ThreadLocalClient:
    def __init__(self):
        self.local = threading.local()

    def __call__(self):
        if not hasattr(self.local, "client"):
            self.local.client = OpenAI(
                api_key="sk-71bbd7d4dce44c84a00be724db9dbf8f",
                base_url="https://api.deepseek.com",
                timeout=REQUEST_TIMEOUT
            )
        return self.local.client


get_client = ThreadLocalClient()


def api_task(thread_id):
    client = get_client()
    messages = [
        {"role": "system", "content": "你的职责是完成我的要求"},
        {"role": "user", "content": "请生成包含魔法森林冒险的英文故事及中文翻译，格式要求与之前示例完全相同"}
    ]

    try:
        start = time.perf_counter()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        # 收集结果
        full_content = []
        for chunk in response:
            if content := chunk.choices[0].delta.content:
                full_content.append(content)

        elapsed = time.perf_counter() - start
        with print_lock:
            stats["success"] += 1
            safe_print(f"\n🎉 线程 {thread_id} 成功 | 耗时: {elapsed:.2f}s | 长度: {len(''.join(full_content))}字符")
        return True

    except RateLimitError as e:
        with print_lock:
            stats["rate_limited"] += 1
            safe_print(f"\n⏳ 线程 {thread_id} 触发速率限制 | 状态码: {e.status_code}")
        return False

    except Exception as e:
        with print_lock:
            stats["errors"] += 1
            safe_print(f"\n❌ 线程 {thread_id} 错误 | {str(e)}")
        return False


if __name__ == '__main__':
    stats["start_time"] = time.perf_counter()

    with ThreadPoolExecutor(max_workers=THREAD_NUM) as executor:
        futures = [executor.submit(api_task, i + 1) for i in range(THREAD_NUM)]
        results = [f.result() for f in futures]

    stats["end_time"] = time.perf_counter()

    # 打印统计报告
    total_time = stats["end_time"] - stats["start_time"]
    safe_print("\n" + "=" * 40)
    safe_print(f"🔍 诊断报告")
    safe_print(f"总耗时: {total_time:.2f}秒")
    safe_print(f"并发请求: {THREAD_NUM} 线程")
    safe_print(f"成功: {stats['success']} | 限速: {stats['rate_limited']} | 错误: {stats['errors']}")
    safe_print("=" * 40)