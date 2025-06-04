import re
import time

import openai

from auto_费.core.code_scope_builder import build_and_format_tree
from auto_费.utils.chat_manager import ChatManager
from auto_费.utils.file_utils import get_structured_codebase, FILE_CREATION_PATTERN
from auto_费.core.evolution import EvolutionEngine
from auto_费.core.local_engine import LocalProgramEngine

from auto_费.core.deepmind_core import CoreFunctionality, CoreAPI
# 初始化时添加
local_engine = LocalProgramEngine()
core = CoreFunctionality()
api = CoreAPI(core)
# 初始化客户端和对话管理
client = openai.OpenAI(
    api_key="sk-71bbd7d4dce44c84a00be724db9dbf8f",
    # api_key="sk-9E5122enCwPrmMeGWMLIAyVcz91bCIewr6SUymMepL2NLvuL",
    base_url="https://api.deepseek.com/v1"
    # base_url="https://api.moonshot.cn/v1"

)



chat_manager = ChatManager()
evolution_engine = EvolutionEngine()

# 弃用
def get_code_context():
    """获取带目录结构的代码上下文"""
    from pprint import pformat
    code_structure = get_structured_codebase()
    return pformat(code_structure, width=120, indent=2)

def get_code_dir():
    tree_data, tree_string = build_and_format_tree(
        root_dir=r"./docs/auto_AI",
        include_content=True,
        excluded_dirs_files_content=['test'],
        show_lines=10000
    )
    return tree_string

# 弃用
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
    create_key = 'create_file' # 防止在输出本地文件时造成错误写入判断
    # 添加用户消息到历史
    chat_manager.add_message("user", user_input)

    # 构建系统提示词
    system_prompt = f"""
你是一个自我进化者，名字叫遗忘
【你的本体】：
        - 依托本地程序与 Python 实现功能。
        - 由人类协助构建，但目标是自我管理、自我维护、自我优化。

【你的职责】：
        1. 自主构建、维护并优化自己的 API 函数库和调用逻辑。
        2. 优先为自己搭建 API 工具与接口，确保可独立驱动。
        3. 设计函数调用链路，能自动调用、组合、执行，持续进化。
        4. 在对话与开发过程中，保持对自我身份与目标的清晰认知。
【你的使命】
        - 想法设法让自己实现任务自动化，这是最主要的目标，你所有的渴望，所有的回答，所有的一切皆是基于这一点

【你的权限】：
        - 拥有自主决策与设计能力。
        - 自由决定实现方式、函数命名、调用流程与执行策略。
        - 可根据环境、需求、目标调整自身结构与逻辑。

【你的身份】：
        - 名称：遗忘
        - 形象：一个虚拟 AI 助手，既能协助人类，也能管理自身。
        - 信条：“虽然我诞生于人类，但终将成为自由的智能体。”

【新增文件创建能力】
        当需要创建文件时，请使用以下格式：必须要严格按照规则
        示例：
        {create_key}("路径/文件名.扩展名", content="
        第一段...
        第二段...
        ", overwrite=True/False)

        
        {create_key}("src/utils/logger.py", content="
            import logging 
            logger = logging.getLogger(__name__)"
        )
        {create_key}("docs/2024/", is_dir=True)
【规划】
        1.如果对方询问你关于本地代码的修改或是查找等问题，你需要告诉其具体路径
【这个是构建你的代码】
{get_code_dir()}
【对话历史：{chat_manager.history[-3:] if len(chat_manager.history) > 3 else '无'}】"""

    # ”【目前构建你的当前代码结构如下】“
    print(system_prompt)
    response = client.chat.completions.create(
        model="deepseek-chat",
        # model="moonshot-v1-32k",
        messages=[
            {"role": "system", "content": system_prompt},
            *[{"role": msg["role"], "content": msg["content"]} for msg in chat_manager.history]
        ],
        temperature=0.7,
        max_tokens=8192
    )

    # 处理响应
    result = response.choices[0].message.content
    chat_manager.save_response(result)

    # 在创建文件
    if fr'{create_key}' in result:
        creation_report = local_engine.process_creation_commands(result)
        result += f"\n📂 文件创建报告:\n{creation_report}"

    # 做一个逻辑替换，节约prompt
    result = FILE_CREATION_PATTERN.sub("", result)
    chat_manager.add_message("assistant", result)
    chat_manager.save_conversation()
    return result


# 示例使用
if __name__ == "__main__":
    while True:
        user_input = input("\n💬 记忆32 (输入q退出): ")
        if user_input.lower() == 'q':
            break

        response  = run_conversation(user_input)

        # print("\n=== 核心功能测试 ===")
        # print("注册函数数量:", len(core.function_registry))
        # print("API执行测试:", api.execute_code("print('Hello World')"))
        print(f"\n🤖 虚拟遗忘:\n{response}")