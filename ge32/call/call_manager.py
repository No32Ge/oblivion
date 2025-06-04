from auto_费.call.function.MusicPlayer import MusicPlayer


class CallManager:
    def __init__(self):
        # 初始化音乐播放器（可选）
        self.music_player = None

    def execute_tool(self, tool_name, arguments):
        """执行工具调用"""
        if tool_name == "play_music":
            # 调用音乐播放功能
            return self._play_music(arguments)
        else:
            return f"未知工具调用: {tool_name}"

    def _play_music(self, arguments):
        """播放音乐的具体实现"""
        try:
            file_path = arguments.get("file")
            volume = arguments.get("volume", 1.0)  # 默认音量为1.0

            # 初始化音乐播放器
            self.music_player = MusicPlayer(file_path, volume=volume)
            result = self.music_player.play()
            return f"音乐播放成功: {result}"
        except Exception as e:
            return f"音乐播放失败: {str(e)}"