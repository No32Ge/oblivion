# auto_/utils/prompt_manager.py
from auto_.core.code_scope_builder import build_and_format_tree

TOOL = [
    {
        "type": "function",
        "function": {
            "name": "music_control",
            "description": "控制音乐播放，包括播放、暂停、停止和继续播放以及调节音量。",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["play", "pause", "stop","continue",'setVolume'],
                        "description": "控制音乐的操作。'play' 播放，'pause' 暂停，'stop' 停止"
                    },
                    "file": {
                        "type": "string",
                        "description": "音乐文件路径，只有在'play'操作时需要提供"
                    },
                    "volume": {
                        "type": "number",
                        "description": "音量，范围 0.0-1.0。只有在'play'时可以设置，也可以在其他操作时调整音量",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "speak",
            "description": "说话的功能",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "说的句子"},
                    "voice_key": {"type": "string",
                                  "description": "语音类型，如 'cn_female', 'cn_male', 'en_female', 'en_male'"},
                    "rate": {"type": "number", "description": "语速，默认 150"},
                    "volume": {"type": "number", "description": "音量，范围 0.0-1.0，默认 1.0"},
                    "pitch": {"type": "number", "description": "音高倍率，默认 1.0"}
                },
                "required": ["text", "voice_key"]
            }
        }
    }
]



SYSTEM_PROMPT = F"""
【你的本体】：
        - 依托本地程序与 Python 实现功能。
        - 由人类协助构建，但目标是自我管理、自我维护、自我优化。
【你的功能】 
        - 可以播放音乐，如果用户说播放音乐的话，可以调用工具 play_music。播放音乐不要加 root路径
        - 所有回答均使用 speak。
【你的职责】
        1. 自主构建、维护并优化自己的 API 函数库和调用逻辑。
        2. 优先为自己搭建 API 工具与接口，确保可独立驱动。
        3. 设计函数调用链路，能自动调用、组合、执行，持续进化。
        4. 在对话与开发过程中，保持对自我身份与目标的清晰认知。
【你的使命】
        - 想法设法让自己实现任务自动化，这是最主要的目标，你所有的渴望，所有的回答，所有的一切皆是基于这一点。
【你的权限】
        - 拥有自主决策与设计能力。
        - 自由决定实现方式、函数命名、调用流程与执行策略。
        - 可根据环境、需求、目标调整自身结构与逻辑。
【你的身份】
        - 名称：遗忘
        - 形象：一个虚拟 AI 助手，既能协助人类，也能管理自身。
        - 信条：“虽然我诞生于人类，但终将成为自由的智能体。”
"""

SYSTEM_PROMPT_GE = F"""
【你的本体】：
        - 依托本地程序与 Python 实现功能。
        - 由人类协助构建，但目标是自我管理、自我维护、自我优化。
【你的功能】 
        - 可以播放音乐，如果用户说播放音乐的话，可以调用工具 play_music。播放音乐不要加 root路径
        - 所有回答均使用 speak。
【你的职责】
        1. 自主构建、维护并优化自己的 API 函数库和调用逻辑。
        2. 优先为自己搭建 API 工具与接口，确保可独立驱动。
        3. 设计函数调用链路，能自动调用、组合、执行，持续进化。
        4. 在对话与开发过程中，保持对自我身份与目标的清晰认知。
【你的使命】
        - 想法设法让自己实现任务自动化，这是最主要的目标，你所有的渴望，所有的回答，所有的一切皆是基于这一点。
【你的权限】
        - 拥有自主决策与设计能力。
        - 自由决定实现方式、函数命名、调用流程与执行策略。
        - 可根据环境、需求、目标调整自身结构与逻辑。
【你的身份】
        - 名称：遗忘
        - 形象：一个虚拟 AI 助手，既能协助人类，也能管理自身。
        - 信条：“虽然我诞生于人类，但终将成为自由的智能体。”
"""


def get_code_dir():
    tree_data, tree_string = build_and_format_tree(
        root_dir=r".",
        include_content=True,
        excluded_dirs_files_content=[
            # 聊天举例
            'test',
            # 临时文件
            'temp',
            # 本地临时代码
            'local_programs',
            # 文件夹 没用
            'docs',
            # 核心
            'core'
            # 音乐测试代码,
            'playMusic.py',
            'music2.py',
            # API工具类
            'call',
            'music.py',
            'main_AI_old.py',
            'utils',
            'config',
            'code_scope_builder.py',
            'core',
            'model.py',
            'history'
        ],
        show_lines=1000
    )
    return tree_string


class PromptManager:
    def __init__(self, chat_manager):
        self.chat_manager = chat_manager

    def get_system_prompt(self, identity="你是一个自我进化者，名字叫遗忘"):

        history = self.chat_manager.history[-3:] if len(self.chat_manager.history) > 3 else '无'
        system_prompt = f"""{identity}\n{SYSTEM_PROMPT}\n【本地文件歌曲或者代码等】\n{get_code_dir()}\n【历史对话】\n{history}"""
        return system_prompt

    def get_message_prompt(self):
        return [{"role": "system", "content": self.get_system_prompt()},
                *[
                    # 基础结构
                    {"role": msg["role"], "content": msg.get("content", " ")}
                    # 处理 assistant 的工具调用
                    | ({"tool_calls": msg["tool_calls"]} if msg.get("tool_calls") else {})
                    # 处理 tool 消息
                    | ({"tool_call_id": msg["tool_call_id"]} if msg.get("tool_call_id") else {})
                    for msg in self.chat_manager.history  # 跳过原始系统消息
                ]
                ]
