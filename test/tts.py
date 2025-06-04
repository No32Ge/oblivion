import pyttsx3


def set_voice(engine, voice_name=None, rate=150, volume=1.0, pitch=1.0):
    """
    设置语音引擎的音色、语速、音量和音高。
    """
    # 设置语速
    engine.setProperty('rate', rate)

    # 设置音量
    engine.setProperty('volume', volume)

    # 获取可用语音列表
    voices = engine.getProperty('voices')

    # 根据传入的语音名称选择语音
    for voice in voices:
        if voice_name in voice.name:
            engine.setProperty('voice', voice.id)
            break

    # 音高的调整（pyttsx3没有直接支持音高，但你可以通过音速来间接控制）
    engine.setProperty('rate', int(rate * pitch))  # 基于音高控制语速


def speak(engine, text):
    """
    使用设置好的语音引擎播放语音。
    """
    engine.say(text)
    engine.runAndWait()  # 等待语音播放完毕


if __name__ == '__main__':
    engine = pyttsx3.init()  # 初始化语音引擎

    # 选择不同语言的语音
    # 选择中文语音
    set_voice(engine, voice_name="Microsoft Huihui Desktop")  # 设置为简体中文
    speak(engine, "你好，我可以说中文")

    # 选择英文语音
    set_voice(engine, voice_name="Microsoft Zira Desktop")  # 设置为英语
    speak(engine, "Hello, I can speak English.")

    # 选择另一种中文语音
    set_voice(engine, voice_name="Microsoft Hanhan Desktop")  # 设置为台湾中文
    speak(engine, "我也能说台湾话。")

    # 选择不同语音的语言输出
    set_voice(engine, voice_name="Microsoft David Desktop")  # 设置为英文男性
    speak(engine, "Now I am speaking with a male voice.")
