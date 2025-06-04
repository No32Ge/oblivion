import json
from datetime import datetime
from auto_费.utils.file_utils import save_file


class ChatManager:
    def __init__(self, storage_dir="test/responses"):
        self.storage_dir = storage_dir
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history = []
        self.memory_cache = set()

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

    def _is_important_tool_call(self, tool_name, result):
        """判断工具调用是否重要"""
        return tool_name in ["play_music", "create_file"]  # 示例：仅记录特定工具调用

    def _summarize_tool_call(self, tool_name, arguments, result):
        """生成工具调用摘要"""
        return f"{tool_name}({arguments}) -> {result[:100]}..."  # 截取结果前100字符

    def get_tool_call_history(self, tool_name=None):
        """获取工具调用历史"""
        if tool_name:
            return {k: v for k, v in self.tool_call_registry.items() if v["tool_name"] == tool_name}
        return self.tool_call_registry