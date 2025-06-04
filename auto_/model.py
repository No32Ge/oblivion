import json
import time

import openai
from sympy.physics.units import sr

from auto_.call.call_manager import CallManager
from auto_.config.API import MODEL_CONFIGS
from auto_.config.prompt_config import TOOL, PromptManager, get_code_dir
from auto_.utils.chat_manager import EnhancedChatManager
from auto_.core.evolution import EvolutionEngine
from auto_.core.deepmind_core import CoreFunctionality, CoreAPI
from test.语音转文本.stt import  get_vosk_mic_transcriber_instance


class ConversationManager:
    def __init__(self, model_name="glm-4-plus"):
        # 加载模型配置
        self.model_config = MODEL_CONFIGS.get(model_name)
        if not self.model_config:
            raise ValueError(f"Unsupported model: {model_name}")

        # 初始化所需的模块和工具
        self.core = CoreFunctionality()
        self.api = CoreAPI(self.core)
        self.client = openai.OpenAI(
            api_key=self.model_config["API_KEY"],
            base_url=self.model_config["BASE_URL"]
        )
        self.call_manager = CallManager()
        self.chat_manager = EnhancedChatManager()
        self.evolution_engine = EvolutionEngine()

    def run_conversation(self, user_input):
        """执行对话流程"""
        # 添加用户消息到历史
        self.chat_manager.add_message("user", user_input)

        # 构建系统提示词
        prompt_manager = PromptManager(self.chat_manager)

        # 与 OpenAI 进行对话，获取响应
        response = self.client.chat.completions.create(
            model=self.model_config["MODEL_NAME"],
            messages=prompt_manager.get_message_prompt(),
            temperature=0.7,
            max_tokens=8192,
            tools=TOOL,
            tool_choice="auto"
        )

        # print("message：" + str(response.choices[0].message))

        # 处理工具调用
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:

            for call in tool_calls:
                tool_name = call.function.name
                arguments = json.loads(call.function.arguments)
                result = self.call_manager.execute_tool(tool_name, arguments)
                self.chat_manager.add_tool_call(tool_calls, result=result)
            time.sleep(5)
            # 第二次把 tool 结果给 assistant 看
            follow_up_response = self.client.chat.completions.create(
                model=self.model_config["MODEL_NAME"],
                messages=prompt_manager.get_message_prompt(),
                temperature=0.7,
                max_tokens=8192,
                tools=TOOL,
                tool_choice="auto"
            )
            final_result = follow_up_response.choices[0].message.content
            self.chat_manager.add_message("assistant", final_result)
            self.chat_manager.save_conversation()

            return final_result

        # 直接处理响应
        result = response.choices[0].message.content
        self.chat_manager.save_response(result)
        self.chat_manager.add_message("assistant", result)
        self.chat_manager.save_conversation()
        return result



# 示例使用
if __name__ == "__main__":
    # 创建 ConversationManager 实例，指定使用的模型（例如 "glm-4-plus"）
    # deepseek
    # transcriber =  get_vosk_mic_transcriber_instance()
    conversation_manager = ConversationManager(model_name="glm-4-plus")
    while True:
        user_input = input("输入内容")
        if user_input.lower() == 'q':
            break

        response = conversation_manager.run_conversation(user_input)

        print(f"\n🤖 虚拟遗忘:\n{response}")
