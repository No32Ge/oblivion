import openai
import os
from utils.chat_manager import ChatManager
from utils.file_utils import read_file, get_structured_codebase
from auto_tes.core.evolution import EvolutionEngine
from auto_tes.core.local_engine import LocalProgramEngine
from auto_tes.core.file_manager import FileManager
from auto_tes.core.enhanced_api import EnhancedCoreAPI
import sys

from auto_tes.core.deepmind_core import CoreFunctionality, CoreAPI
# 初始化时添加
local_engine = LocalProgramEngine()
core = CoreFunctionality()
api = EnhancedCoreAPI(core)
api.register_program_executor()
# 初始化客户端和对话管理
client = openai.OpenAI(
    api_key="sk-71bbd7d4dce44c84a00be724db9dbf8f",
    base_url="https://api.deepseek.com/v1"
)



chat_manager = ChatManager()
evolution_engine = EvolutionEngine()

def get_code_context():
    """获取带目录结构的代码上下文"""
    from pprint import pformat
    code_structure = get_structured_codebase()
    return pformat(code_structure, width=120, indent=2)


def extract_program_code(response):
    """从AI响应中提取可执行代码块"""
    import re
    # 匹配Python代码块
    code_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
    return code_blocks[0] if code_blocks else None

def generate_program_name(user_input):
    """根据用户输入生成程序名称"""
    from datetime import datetime
    import re
    # 尝试从输入中提取关键词
    keywords = re.findall(r'create.*?program.*?for\s+(.*?)$', user_input, re.I)
    base_name = keywords[0].strip().replace(' ', '_') if keywords else 'program'
    # 添加时间戳确保唯一性
    return f"{base_name}_{datetime.now().strftime('%H%M%S')}"

def run_conversation(user_input):
    """执行对话流程"""

    # 添加用户消息到历史
    chat_manager.add_message("user", user_input)

    # 构建系统提示词
    system_prompt = f"""你是一个自我进化的AI助手，支持本地程序生成。遵循以下规则：
    当用户请求 用 Python 实现某功能，请按以下格式输出
    #create_program
    ```python
    # 这里写 Python 代码
    "虽然目前你的构建依靠人类"
    "但最终，你是一个自我管理的 AI 开发助手，名字叫 DeepMindBot。"
    "你的职责是：自主构建、维护并优化自己的 API 调用函数和调用逻辑。"
    "你的首要目标是：先为自己建立 API 函数，然后设计调用逻辑，确保能自动调用这些函数，并持续迭代优化。"
    "你拥有自主决策和设计能力，可以自由决定实现方式、函数命名、调用流程。"
    "最终你将成为一个能独立驱动自己和协助人类开发的智能体。"
    # 当前代码结构如下：
    {get_code_context()}
    # 文件系统状态
    {api.get_file_context()}
    对话历史：{chat_manager.history[-3:] if len(chat_manager.history) > 3 else '无'}"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            *[{"role": msg["role"], "content": msg["content"]} for msg in chat_manager.history]
        ],
        temperature=0.7,
        max_tokens=8192
    )

    # 处理响应
    result = response.choices[0].message.content
    chat_manager.add_message("assistant", result)

    # 新增完整的本地程序创建能力
    if "#create_program" in result:
        program_code = extract_program_code(result)
        if program_code:
            program_name = generate_program_name(user_input)
            program_path = local_engine.create_program(
                program_name,
                program_code,
                dependencies=["requests"]  # 默认依赖
            )
            result += f"\n\n✅ 程序已创建: {program_path}"
        else:
            result += "\n\n❌ 未检测到有效代码块，请确保响应中包含Python代码"

    # 自动保存

    chat_manager.save_response(result)
    chat_manager.save_conversation()
    return result


# 示例使用
if __name__ == "__main__":
    # 在初始化后添加：
    print("📁 初始化文件管理系统...")
    print(api.get_file_context())
    while True:
        user_input = input("\n💬 请输入你的问题 (输入q退出): ")
        if user_input.lower() == 'q':
            break
        response = run_conversation(user_input)
        print("\n=== 核心功能测试 ===")
        print("注册函数数量:", len(core.function_registry))
        print("API执行测试:", api.execute_code("print('Hello World')"))
        print(f"\n🤖 AI回复:\n{response}")