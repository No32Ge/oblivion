#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 安全标识：NO_FILE_OPERATION
PROGRAM_TEMPLATES = {
    "data_processor": {
        "description": "通用数据处理程序",
        "template": """import pandas as pd

def process_data(input_file, output_file):
    df = pd.read_csv(input_file)
    # 数据处理逻辑
    df.to_csv(output_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    process_data(args.input, args.output)
""",
        "dependencies": ["pandas"]
    },
    "web_scraper": {
        "template": """import requests
from bs4 import BeautifulSoup
# ...网页抓取模板...
"""
    }
}

PROGRAM_TEMPLATES.update({
    "playMusic": {
        "description": "播放音乐",
        "needs_sandbox": False,  # 基础功能无需沙箱
        "template": '''#!/usr/bin/env python3
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
'''
    }
})