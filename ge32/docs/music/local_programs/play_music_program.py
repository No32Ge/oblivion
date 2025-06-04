
import pygame
import time

def play_music(audio_file):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

if __name__ == "__main__":
    play_music(r"D:\Ge\code\python\deepseek\auto_\Grimes - Oblivion.ogg")
