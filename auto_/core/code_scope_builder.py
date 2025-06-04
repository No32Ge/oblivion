import os

def build_directory_tree(root_dir=".", include_content=False, excluded_dirs_files_content=None):
    """递归构建目录树结构，可选是否包含文件内容和排除指定目录"""
    text_extensions = (".py", ".js", ".html", ".css", ".md", ".json",".txt")
    binary_extensions = (".mp3", ".mp4", ".wav",".ogg",'music.py')

    def build_tree(current_path, relative_path=""):
        tree = {}
        for entry in os.listdir(current_path):
            entry_path = os.path.join(current_path, entry)
            sub_relative_path = os.path.join(relative_path, entry)

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

def format_tree(tree, indent="", show_lines=None):
    """格式化树状结构，返回字符串"""
    lines = []

    for key, value in tree.items():
        lines.append(f"{indent}├── {key}")
        if isinstance(value, dict):
            sub_lines = format_tree(value, indent + "│   ", show_lines)
            lines.extend(sub_lines)
        elif isinstance(value, str) and value is not None:
            content_lines = value.strip().splitlines()
            if show_lines is None:
                preview = [f"{indent}│   {line}" for line in content_lines]
            else:
                preview = [f"{indent}│   {line}" for line in content_lines[:show_lines]]
                if len(content_lines) > show_lines:
                    preview.append(f"{indent}│   ... ({len(content_lines)} lines)")
            lines.extend(preview)
    return lines

def  build_and_format_tree(root_dir=".", include_content=False, excluded_dirs_files_content=None, show_lines=None):
    """组合构建+格式化目录树，返回 (树结构, 格式化字符串)"""
    tree = build_directory_tree(
        root_dir=root_dir,
        include_content=include_content,
        excluded_dirs_files_content=excluded_dirs_files_content
    )
    formatted_lines = format_tree(tree, show_lines=show_lines)
    formatted_string = "\n".join(formatted_lines)
    return tree, formatted_string

# 示例调用
if __name__ == "__main__":
    # 使用方法
    tree_data, tree_string = build_and_format_tree(
        root_dir=".",
        include_content=True,
        excluded_dirs_files_content=['音乐', '小说'],
        show_lines=100
    )

    print("====== 树结构数据 ======")
    print(tree_data)
    print("\n====== 树结构格式化字符串 ======")
    print(tree_string)
