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

    def save_response(self, response, category="general"):
        """单独保存AI响应"""
        filename = f"{category}_{datetime.now().strftime('%H%M%S')}.txt"
        return save_file(response, self.storage_dir, filename)


class EnhancedMemory(ChatManager):
    def __init__(self, max_history=30):  # 记忆容量从20→30
        super().__init__()
        self.long_term = []  # 新增长期记忆存储
        self.cache_size = 100  # 新增缓存容量

    def add_message(self, role, content):
        """增强版消息添加"""
        super().add_message(role, content)
        if self._is_important(content):  # 新增重要性判断
            self.long_term.append(self._summarize(content))