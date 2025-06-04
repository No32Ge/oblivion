import pyttsx3


class Speak:
    def __init__(self, voice_key=None, rate=150, volume=1.0, pitch=1.0):
        self.model = {
            "cn_female": "Microsoft Huihui Desktop",
            "cn_male": "Microsoft Hanhan Desktop",
            "en_female": "Microsoft Zira Desktop",
            "en_male": "Microsoft David Desktop"
        }
        self.engine = pyttsx3.init()
        self.voice_key = voice_key
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self.set_voice()

    def set_voice(self):
        """
        设置语音引擎的音色、语速、音量和音高。
        """
        self.engine.setProperty('volume', self.volume)
        voices = self.engine.getProperty('voices')

        if self.voice_key:
            target_voice_name = self.model.get(self.voice_key)
            if target_voice_name:
                for voice in voices:
                    if target_voice_name in voice.name:
                        self.engine.setProperty('voice', voice.id)
                        break
            else:
                print(f"未找到 voice_key: {self.voice_key} 对应的语音配置")

        self.engine.setProperty('rate', int(self.rate * self.pitch))

    def speak(self, text):
        """
        使用设置好的语音引擎播放语音。
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()

            # 判断是中文还是英文
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                display_text = text[:10] + "..." if len(text) > 10 else text
            else:
                words = text.split()
                display_text = " ".join(words[:10]) + "..." if len(words) > 10 else text

            result = f"正在说话: {display_text}"
            print(result)
            return result

        except Exception as e:
            error_message = f"语音播放失败: {str(e)}"
            print(error_message)
            return error_message
