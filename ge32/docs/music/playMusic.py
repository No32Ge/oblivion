#!/usr/bin/env python3
# -*- coding: gbk -*-
import subprocess
import sys
import os
import uuid


class ProgramExecutor:
    def __init__(self, program_dir="local_programs"):
        self.program_dir = program_dir  # �洢�����ļ���Ŀ¼
        os.makedirs(self.program_dir, exist_ok=True)  # ȷ������Ŀ¼����

    def execute_python_program(self, code, program_name=None, dependencies=None, args=None):
        """������ִ�б��� Python ����"""
        program_name = program_name or f"program_{uuid.uuid4()}"  # Ĭ��ʹ��Ψһ���ļ���
        program_path = self.create_program(program_name, code, dependencies)

        # ִ�иó���
        return self.execute_local_python(program_path, args)

    def execute_local_python(self, file_path, args=None):
        """ִ�б��� Python ����"""
        if not os.path.exists(file_path):
            return {"error": f"�ļ� {file_path} ������"}

        cmd = [sys.executable, file_path]  # ʹ�õ�ǰ Python ���������нű�
        if args:
            cmd.extend(args)  # ����д��ݲ�������ӵ�������

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return {
            "exit_code": result.returncode,  # �����˳���
            "output": result.stdout,  # ��׼���
            "error": result.stderr  # ������Ϣ
        }

    def create_program(self, program_name, code, dependencies=None):
        """����һ����ִ�е� Python ����"""
        program_path = os.path.join(self.program_dir, f"{program_name}.py")

        # д�� Python �������
        with open(program_path, "w") as file:
            file.write(code)

        # �Զ���װ����
        if dependencies:
            self._install_dependencies(dependencies)

        return program_path

    def _install_dependencies(self, packages):
        """�Զ���װ����"""
        subprocess.run([sys.executable, "-m", "pip", "install"] + packages)


# ʾ���÷�
if __name__ == "__main__":
    executor = ProgramExecutor()

    # ���� Python ������루���粥����Ƶ�ĳ���
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
    # ������ִ�г���
    result = executor.execute_python_program(program_code, dependencies=["pygame"])

    # ��ӡִ�н��
    print("Exit Code:", result['exit_code'])
    print("Output:", result['output'])
    print("Error:", result['error'])
