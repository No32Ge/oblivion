import os
import re

# 未测试
from pathlib import Path

FILE_CREATION_PATTERN = re.compile(r"""
create_file\(                                           
    \s*['"](?P<path>[^'"]+)['"]                         
    (?:,\s*content=(?P<quote>['"]{1,3})(?P<content>.*?)(?P=quote)
        (?:,\s*overwrite=(?P<overwrite>True|False))?     
    )?
    \s*\)                                               
""", re.VERBOSE | re.DOTALL)

############# 新
def create_files(file_structures):
    """在原有 save_file 函数下方添加"""
    results = []
    for fs in file_structures:
        path = Path(fs['path'])

        try:
            # 处理目录创建
            if fs.get('is_dir'):
                path.mkdir(parents=True, exist_ok=True)
                results.append(f"📁 创建目录: {path}")
                continue

            # 处理文件存在性检查
            if path.exists() and not fs.get('overwrite', False):
                results.append(f"⏩ 跳过已存在文件: {path}")
                continue

            # 创建父目录并写入文件
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(fs.get('content', ''))
            results.append(f"✅ 创建文件: {path}")

        except Exception as e:
            results.append(f"❌ 创建失败 [{path}]: {str(e)}")

    return results

################

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

