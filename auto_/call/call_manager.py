from auto_.call.function.MusicPlayer import MusicPlayer
from auto_.call.function.Speak import Speak


class CallManager:
    def __init__(self):
        # 初始化音乐播放器（可选）
        self.music_player = None
        self.speaker = None

    def execute_tool(self, tool_name, arguments):
        """执行工具调用"""
        if tool_name == "music_control":
            return self._play_music(arguments)
        elif tool_name == "speak":
            return self._speak(arguments)
        else:
            return f"未知工具调用: {tool_name}"

    def _play_music(self, arguments):
        """控制音乐播放，包括播放、暂停、停止、继续播放和调节音量"""
        try:
            action = arguments.get("action")
            result = None

            # 如果是播放音乐
            if action == 'play':
                file_path = arguments.get("file")
                volume = arguments.get("volume", 1.0)  # 默认音量为 1.0
                if not file_path:
                    return "音乐文件路径不能为空"
                # 初始化音乐播放器
                self.music_player = MusicPlayer(file_path, volume=volume)
                result = self.music_player.play()
                return f"音乐播放成功: {result}"

            # 如果是暂停音乐
            elif action == 'pause':
                if hasattr(self, 'music_player') and self.music_player.is_playing:
                    result = self.music_player.pause()
                    return f"音乐暂停: {result}"
                else:
                    return "没有正在播放的音乐，无法暂停"

            # 如果是停止音乐
            elif action == 'stop':
                if hasattr(self, 'music_player') and self.music_player.is_playing:
                    result = self.music_player.stop()
                    return f"音乐停止: {result}"
                else:
                    return "没有正在播放的音乐，无法停止"

            # 如果是继续播放
            elif action == 'continue':
                if hasattr(self, 'music_player') and self.music_player.is_paused:
                    result = self.music_player.resume()
                    return f"继续播放: {result}"
                else:
                    return "没有暂停的音乐，无法继续播放"

            # 如果是设置音量
            elif action == 'setVolume':
                volume = arguments.get("volume")
                if volume is not None:
                    if 0.0 <= volume <= 1.0:
                        result = self.music_player.set_volume(volume)
                        return f"音量设置成功: {result}"
                    else:
                        return "音量值必须在 0.0 到 1.0 之间"
                else:
                    return "请提供音量值"

            else:
                return "无效的操作，支持的操作有: play, pause, stop, continue, setVolume"

        except Exception as e:
            return f"音乐控制失败: {str(e)}"

    def _speak(self, arguments):
        """语音播放的具体实现"""
        try:
            text = arguments.get("text")
            voice_key = arguments.get("voice_key", "cn_female")
            rate = arguments.get("rate", 150)
            volume = arguments.get("volume", 1.0)
            pitch = arguments.get("pitch", 1.0)

            self.speaker = Speak(voice_key=voice_key, rate=rate, volume=volume, pitch=pitch)
            result = self.speaker.speak(text)
            return f"说话成功: {result}"
        except Exception as e:
            return f"说话失败: {str(e)}"

