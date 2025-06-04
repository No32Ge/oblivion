#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
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
        self.is_playing = False  # 音乐是否正在播放
        self.is_paused = False  # 音乐是否暂停

        # 获取当前工作目录
        self.current_dir = os.getcwd()
        # 生成音频文件的完整路径
        self.audio_file_path = os.path.join(self.current_dir, self.audio_file_name)

        # 初始化 pygame 混音器
        pygame.mixer.init()

    def play(self):
        """播放音频"""
        if not self.is_playing:
            # 设置音量
            pygame.mixer.music.set_volume(self.volume)

            # 播放音频
            pygame.mixer.music.load(self.audio_file_path)
            pygame.mixer.music.play()

            self.is_playing = True
            self.is_paused = False
            return "播放中"
        else:
            return "音乐已经在播放"

    def stop(self):
        """停止播放"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            return "音乐停止"
        return "没有播放任何音乐"

    def pause(self):
        """暂停播放"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            return "音乐暂停"
        return "音乐未播放或已暂停"

    def resume(self):
        """继续播放"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            return "继续播放"
        return "音乐未暂停，无法继续播放"

    def set_volume(self, volume):
        """设置音量"""
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            pygame.mixer.music.set_volume(self.volume)
            return f"音量已设置为 {volume * 100}%"
        return "音量设置无效，请提供0.0到1.0之间的值"

# 示例使用
if __name__ == "__main__":
    player = MusicPlayer("your_audio_file.mp3")  # 替换为实际的音频文件路径

    print(player.play())        # 播放音乐
    print(player.set_volume(0.5))  # 调节音量为50%
    print(player.pause())       # 暂停播放
    print(player.resume())      # 继续播放
    print(player.stop())        # 停止播放
