import os


def run_music_cmd():
    # 调用命令行并执行 Python 脚本
    command = r'''D:\Python39\python.exe D:/Ge/code/python/deepseek/auto_broke/music.py "D:/Ge/code/python/deepseek/auto_broke/Grimes - Oblivion.ogg"'''

    # 去掉 pause 尝试直接执行
    os.system(f'start cmd /k "{command}"')


if __name__ == "__main__":
    run_music_cmd()
