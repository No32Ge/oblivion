#!/usr/bin/env python3
# -*- coding: gbk -*-
import subprocess
import sys
import os
import uuid


class ProgramExecutor:
    def __init__(self, program_dir="local_programs"):
        self.program_dir = program_dir  # 存储程序文件的目录
        os.makedirs(self.program_dir, exist_ok=True)  # 确保程序目录存在

    def execute_python_program(self, code, program_name=None, dependencies=None, args=None):
        """创建并执行本地 Python 程序"""
        program_name = program_name or f"program_{uuid.uuid4()}"  # 默认使用唯一的文件名
        program_path = self.create_program(program_name, code, dependencies)

        # 执行该程序
        return self.execute_local_python(program_path, args)

    def execute_local_python(self, file_path, args=None):
        """执行本地 Python 程序"""
        if not os.path.exists(file_path):
            return {"error": f"文件 {file_path} 不存在"}

        cmd = [sys.executable, file_path]  # 使用当前 Python 解释器运行脚本
        if args:
            cmd.extend(args)  # 如果有传递参数，添加到命令中

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return {
            "exit_code": result.returncode,  # 返回退出码
            "output": result.stdout,  # 标准输出
            "error": result.stderr  # 错误信息
        }

    def create_program(self, program_name, code, dependencies=None):
        """创建一个可执行的 Python 程序"""
        program_path = os.path.join(self.program_dir, f"{program_name}.py")

        # 写入 Python 程序代码
        with open(program_path, "w") as file:
            file.write(code)

        # 自动安装依赖
        if dependencies:
            self._install_dependencies(dependencies)

        return program_path

    def _install_dependencies(self, packages):
        """自动安装依赖"""
        subprocess.run([sys.executable, "-m", "pip", "install"] + packages)


# 示例用法
if __name__ == "__main__":
    executor = ProgramExecutor()

    # 定义 Python 程序代码（比如播放音频的程序）
    program_code = """
import pygame
import time

def play_music(audio_file):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

if __name__ == "__main__":
    play_music(r"D:\\Ge\\code\\python\\deepseek\\auto_broke\\Grimes - Oblivion.ogg")
"""
    # 创建并执行程序
    result = executor.execute_python_program(program_code, dependencies=["pygame"])

    # 打印执行结果
    print("Exit Code:", result['exit_code'])
    print("Output:", result['output'])
    print("Error:", result['error'])
