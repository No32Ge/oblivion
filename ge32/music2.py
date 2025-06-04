import pygame
import time

def play_music(audio_file):
    pygame.mixer.init()  # 初始化音频
    print(f"音频设备状态：{pygame.mixer.get_init()}")  # 输出音频设备初始化状态
    pygame.mixer.music.load(audio_file)  # 加载音频文件
    pygame.mixer.music.play()  # 播放音频

    while pygame.mixer.music.get_busy():  # 等待音频播放完成
        print("音频播放中...")
        time.sleep(1)

if __name__ == "__main__":
    play_music(r"D:\Ge\code\python\deepseek\auto_\Grimes - Oblivion.ogg")
