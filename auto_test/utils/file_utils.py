import os

def read_file(file_path):
    """安全读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None

def save_file(content, dir_path, filename):
    """通用文件保存方法"""
    os.makedirs(dir_path, exist_ok=True)
    try:
        filepath = os.path.join(dir_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return None


def get_structured_codebase(root_dir="."):
    """获取保留目录结构的代码库信息"""
    code_structure = {}
    for root, dirs, files in os.walk(root_dir):
        relative_path = os.path.relpath(root, start=root_dir)
        if relative_path == ".":
            relative_path = "root"

        file_contents = {}
        for file in files:
            if file.endswith((".py", ".js", ".html", ".css", ".md")):
                content = read_file(os.path.join(root, file))
                if content:
                    file_contents[file] = content

        if file_contents:
            code_structure[relative_path] = file_contents

    return code_structure