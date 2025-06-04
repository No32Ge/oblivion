
#!/usr/bin/env python3
# -*- coding: gbk -*-
# ��ȫ��ʶ��NO_FILE_OPERATION
import pygame
import time
import argparse

def play_music(audio_file):
    pygame.mixer.init()  # ��ʼ����Ƶ����
    pygame.mixer.music.load(audio_file)  # ������Ƶ�ļ�
    pygame.mixer.music.play()  # ������Ƶ

    while pygame.mixer.music.get_busy():  # �ȴ���Ƶ�������
        time.sleep(1)
def stop_music():
    pygame.mixer.music.stop()  # ֹͣ��������

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_file", help="Path to the audio file")  # ʹ�� 'audio_file' ��Ϊλ�ò���
    args = parser.parse_args()
