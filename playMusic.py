#!/usr/bin/env python3

import pygame
import time
import argparse

def play_music(audio_file):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)
def stop_music():
    pygame.mixer.music.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_file", help="Path to the audio file")
    args = parser.parse_args()

    play_music(args.audio_file)

