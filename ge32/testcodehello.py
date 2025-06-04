#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import pygame

class MusicPlayer:
    def __init__(self, audio_file_name, sleep_time=0, volume=1.0):
        """
        初始化音乐播放器。

        :param audio_file_name: 音频文件名
        :param sleep_time: 等待音乐播放的时间，默认1500秒
        :param volume: 音量，范围从 0.0 到 1.0，默认最大音量
        """
        self.audio_file_name = audio_file_name
        self.sleep_time = sleep_time
        self.volume = volume

        # 获取当前工作目录
        self.current_dir = os.getcwd()
        # 生成音频文件的完整路径
        self.audio_file_path = os.path.join(self.current_dir, self.audio_file_name)

    def play(self):
        """播放音频"""
        # 初始化 pygame 混音器
        pygame.mixer.init()

        # 设置音量
        pygame.mixer.music.set_volume(self.volume)

        # 播放音频
        pygame.mixer.music.load(self.audio_file_path)
        pygame.mixer.music.play()
        return "播放中"

        # 等待指定时间


    def stop(self):
        """停止播放"""
        pygame.mixer.music.stop()
        return "音乐停止"

if __name__ == '__main__':
    # 音频文件名（确保该文件存在于当前工作目录）
    audio_file_name = r"Grimes - Oblivion.ogg"

    # 创建音乐播放器实例，设置音量为 0.5
    player = MusicPlayer(audio_file_name, volume=0.5)

    # 播放音乐
    player.play()
    print("你好")
    # 假设播放一段时间后停止（例如3秒）
    time.sleep(300)
    player.stop()
