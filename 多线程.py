from openai import OpenAI
from multiprocessing import Process, Queue, current_process
import time, threading

# 多个API Key
api_keys = [
    "sk-71bbd7d4dce44c84a00be724db9dbf8f",
    "sk-6f76cf8306a441259cfa462b22832765",
    "sk-497f472f192946a695a71e8b0680e18f"
]

base_url = "https://api.deepseek.com"

# 调度器，分配key
class Dispatcher:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.index = 0

    def get_key(self):
        key = self.api_keys[self.index % len(self.api_keys)]
        self.index += 1
        return key

def generate_article(prompt, dispatcher, queue):
    api_key = dispatcher.get_key()
    client = OpenAI(api_key=api_key, base_url=base_url)
    process_name = current_process().name

    messages = [
        {"role": "system", "content": "你的职责是完成我的要求"},
        {"role": "user", "content": prompt},
    ]

    print(f"\n[{process_name}] 使用 {api_key} 生成中...")

    try:
        # 发起请求并开始流式接收响应
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        # 用来保存所有返回的内容
        full_response = ""

        # 遍历流中的每个 chunk
        for chunk in response:
            content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, "content") else ""
            if content:
                full_response += content  # 累积所有内容

        # 输出完整的返回内容
        print(f"\n[{process_name}] 完成！生成内容：\n{full_response}")

        # 将结果放入队列
        queue.put((process_name, full_response))

    except Exception as e:
        print(f"\n[{process_name}] 出错: {e}")
        queue.put((process_name, None))

def run_with_dispatcher(prompts):
    dispatcher = Dispatcher(api_keys)
    processes = []
    queue = Queue()

    for prompt in prompts:
        p = Process(target=generate_article, args=(prompt, dispatcher, queue))
        p.start()
        processes.append(p)
        time.sleep(0.3)

    for p in processes:
        p.join()

    while not queue.empty():
        name, result = queue.get()
        print(f"\n【{name} 完成】：{result[:50]}...")

if __name__ == '__main__':
    prompts = [
        "请翻译并生成格式：One day I saw a bird.",
        "请翻译并生成格式：It started raining heavily.",
        "请翻译并生成格式：We found a hidden cave.",
        "请翻译并生成格式：The sun was setting beautifully."
    ]
    run_with_dispatcher(prompts)
