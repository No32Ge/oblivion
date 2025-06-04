import glob
import json
import os
from datetime import datetime
from auto_.utils.file_utils import save_file


class ChatManager:
    def __init__(self, storage_dir="history/responses"):
        self.storage_dir = storage_dir
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history = []
        self.memory_cache = set()
        self.load = False

    def add_message(self, role, content):

        """添加对话记录"""
        content_hash = hash(content)
        if content_hash not in self.memory_cache:
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                "content_hash": content_hash
            })
            self.memory_cache.add(content_hash)
        self.save_conversation()

    def load_conversation(self, conversation_id: str = ""):
        """动态加载指定会话的历史记录"""
        self.conversation_id = self.conversation_id
        filename = f"conversation_{self.conversation_id}.json"
        filepath = os.path.join(self.storage_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.history = json.load(f)

            # 重建内存缓存保证数据一致性
            self.memory_cache = set()
            for msg in self.history:
                if 'content_hash' in msg:
                    self.memory_cache.add(msg['content_hash'])

        except FileNotFoundError:
            raise ValueError(f"会话文件 {filename} 不存在")
        except json.JSONDecodeError:
            raise ValueError(f"会话文件 {filename} 格式错误")

    def list_conversations(self) -> list:
        """获取所有可用会话ID列表"""
        pattern = os.path.join(self.storage_dir, "conversation_*.json")
        return [
            os.path.basename(f)[12:-5]  # 提取日期时间部分
            for f in glob.glob(pattern)
            if os.path.isfile(f)
        ]

    def save_conversation(self):
        """保存完整对话历史"""

        filename = f"conversation_{self.conversation_id}.json"
        return save_file(
            json.dumps(self.history, indent=2, ensure_ascii=False),
            self.storage_dir,
            filename
        )

    def add_tool_call(self, tool_name, arguments, result):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "tool_call",
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result
        })



    def save_response(self, response, category="general"):
        """单独保存AI响应"""
        filename = f"{category}_{datetime.now().strftime('%H%M%S')}.txt"
        return save_file(response, self.storage_dir, filename)


class EnhancedChatManager(ChatManager):
    def __init__(self, max_history=50, long_term_capacity=1000):
        super().__init__()
        self.long_term_memory = []  # 长期记忆存储
        self.tool_call_registry = {}  # 工具调用注册表
        self.max_history = max_history
        self.long_term_capacity = long_term_capacity

    def add_tool_call(self, calls, result):
        # 记录 assistant 发起的 tool_call 消息
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": call.id,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    },
                    "type": call.type,
                    "index": call.index
                } for call in calls
            ]
        })

        # 记录 tool 执行结果
        for call in calls:
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "role": "tool",
                "tool_call_id": call.id,
                "content": result  # 这里可以根据情况不同call结果写不同，这里假设统一 result
            })

        self.save_conversation()
