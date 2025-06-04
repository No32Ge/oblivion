import os


def build_directory_tree(root_dir=".", include_content=False, excluded_dirs_files_content=None):
    """递归构建目录树结构，可选是否包含文件内容和排除指定目录"""

    # 需要读取内容的文本类型
    text_extensions = (".py", ".js", ".html", ".css", ".md",".json")
    # 绝不读取内容的二进制类型
    binary_extensions = (".mp3", ".mp4", ".wav")

    def build_tree(current_path, relative_path=""):
        tree = {}
        for entry in os.listdir(current_path):
            entry_path = os.path.join(current_path, entry)
            sub_relative_path = os.path.join(relative_path, entry)

            # 判断是否在排除目录内
            if excluded_dirs_files_content and any(
                    sub_relative_path.startswith(d) for d in excluded_dirs_files_content):
                continue

            if os.path.isdir(entry_path):
                tree[entry] = build_tree(entry_path, sub_relative_path)
            else:
                if entry.endswith(text_extensions):
                    if include_content:
                        try:
                            with open(entry_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            tree[entry] = content
                        except Exception as e:
                            tree[entry] = f"[读取失败: {e}]"
                    else:
                        tree[entry] = None
                elif entry.endswith(binary_extensions):
                    tree[entry] = "[二进制文件，不显示内容]"
        return tree

    return {'root': build_tree(root_dir)}


def print_tree(tree, indent="", show_lines=None):
    """打印树状结构"""
    for key, value in tree.items():
        print(f"{indent}├── {key}")
        if isinstance(value, dict):
            print_tree(value, indent + "│   ", show_lines)
        elif isinstance(value, str) and value is not None:
            lines = value.strip().splitlines()

            # 根据 show_lines 参数来决定显示多少行内容
            if show_lines is None:
                preview = '\n'.join([f"{indent}│   {line}" for line in lines])  # 显示全部内容
            else:
                preview = '\n'.join([f"{indent}│   {line}" for line in lines[:show_lines]])  # 只显示指定行数
                if len(lines) > show_lines:
                    preview += f"\n{indent}│   ... ({len(lines)} lines)"
            print(preview)


# 示例调用
if __name__ == "__main__":

    directory_tree = build_directory_tree(include_content=True, excluded_dirs_files_content=['音乐', '小说'])
    print_tree(directory_tree,show_lines=0)  # 只显示每个文件的前10行
