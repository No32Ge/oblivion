#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 安全标识：NO_FILE_OPERATION
import argparse
import pygame
import time

def play_music(audio_file):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="file")
    parser.add_argument("--audio_file", required=True, help="url")
    args = parser.parse_args()

    play_music(args.audio_file)
