import os

import docker


class ExecutionSandbox:
    def __init__(self):
        self.client = docker.from_env()

    def safe_execute(self, program_path, timeout=30):
        """在容器中安全执行程序"""
        container = self.client.containers.run(
            "python:3.9-slim",
            f"python {program_path}",
            volumes={os.path.abspath(program_path): {'bind': '/program.py', 'mode': 'ro'}},
            remove=True,
            stdout=True,
            stderr=True,
            timeout=timeout
        )
        return container.logs()