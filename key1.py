# -*- coding: utf-8 -*-

from openai import OpenAI

class DeepSeekAPI:
    def __init__(self, api_key, base_url="https://api.deepseek.com"):
        # 初始化 API 客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_article(self, message: str, level: str = "Intermediate High"):
        # 定义消息结构
        mess = f"""
        请提供以下： {message}文章特定格式的输出，包括文章和翻译，格式如:(注意，根据这里level根据英文部分的难度在ACTFL中选择;其中，有这些选择:         Novice Low、Novice High Intermediate Low、Intermediate Mid、Intermediate High、Advanced Low。Advanced Mid、Advanced High‘Superior)         这是输出格式的示范（请绝对按照要求。否则无法扫描，也就是你所输出的英文部分标点符号或是空格需要完全一模一样，否则无法匹配，我便会一直重复询问；另外，如果json内容中出现"号，请提供转义字符;用代码格式输出）:         {{"{message}": "翻译", "level": "{level}"}}
        """
        # 准备发送的消息
        messages = [
            {"role": "system", "content": "你的职责是完成我的要求"},
            {"role": "user", "content": mess},
        ]

        # 调用 DeepSeek API 生成文章
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False  # 不启用流式返回
        )

        # 获取生成的内容（修正后的访问方式）
        content = response.choices[0].message.content
        return content

# 使用示例
if __name__ == '__main__':
    # 创建 DeepSeekAPI 实例
    api_key = "sk-71bbd7d4dce44c84a00be724db9dbf8f"  # 替换为你的 API Key
    deepseek = DeepSeekAPI(api_key)

    # 生成文章
    message = "One day, while I was playing in the park, I saw a small dog wandering around all by itself."
    generated_article = deepseek.generate_article(message)

    # 打印生成的文章
    print("生成的文章：\n")
    print(generated_article)