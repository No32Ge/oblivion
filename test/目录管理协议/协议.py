import os
import json
import shutil
import sys

class DirProtoManager:
    """
    管理基于目录协议 (dirproto.json) 的文件操作和可见性。

    协议文件 (dirproto.json) 结构示例:
    {
        "inherit_parent": true,  # 是否继承父目录协议 (默认为 false)
        "visible_files": ["file1.txt", "subdir", "script.py"], # 在此目录中可见的文件/子目录列表
        "operable_files": ["file1.txt", "script.py"] # 在此目录中可操作 (编辑/删除/移动源) 的文件列表
    }
    """
    def __init__(self, base_dir):
        """
        初始化 DirProtoManager。
        :param base_dir: 项目的基础根目录路径。
        """
        # 使用绝对路径以保证一致性
        self.base_dir = os.path.abspath(base_dir)
        self.protocols = {} # 存储加载后的协议，键为目录的绝对路径
        print(f"初始化 DirProtoManager，基础目录: {self.base_dir}")
        if not os.path.isdir(self.base_dir):
            print(f"警告: 基础目录 '{self.base_dir}' 不存在或不是一个目录。", file=sys.stderr)
            # 可以考虑在这里抛出异常，如果基础目录不存在则无法继续
            # raise FileNotFoundError(f"未找到基础目录 '{self.base_dir}' 或它不是一个目录")

    # --- 协议文件初始化 ---
    def initialize_protocols_recursive(self, dir_path):
        """
        递归地确保 dir_path 及其所有子目录中都存在 dirproto.json 文件。
        如果文件不存在，则创建内容为 '{}' 的空文件。如果已存在，则跳过。
        (私有辅助方法)
        """
        abs_dir_path = os.path.abspath(dir_path)

        # 安全检查: 仅在 base_dir 内操作
        if not abs_dir_path.startswith(self.base_dir):
            # print(f"跳过初始化基础目录之外的路径: {abs_dir_path}", file=sys.stderr) # 通常不需要打印
            return

        proto_path = os.path.join(abs_dir_path, "dirproto.json")

        # 检查文件是否存在，如果不存在则创建
        if not os.path.exists(proto_path):
            try:
                # 创建空文件并写入 {}
                with open(proto_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f) # 写入空的 JSON 对象
                print(f"已初始化空的协议文件: {proto_path}")
            except OSError as e:
                print(f"错误: 无法创建协议文件 {proto_path}: {e}", file=sys.stderr)
            except Exception as e: # 捕捉其他潜在错误
                 print(f"错误: 创建协议文件 {proto_path} 时发生意外错误: {e}", file=sys.stderr)
        # else: # 文件已存在，不做任何事
        #    pass

        # 递归进入子目录
        try:
            # 使用 scandir 可能性能更好
            for entry in os.scandir(abs_dir_path):
                if entry.is_dir():
                    # 对子目录递归调用自身
                    self.initialize_protocols_recursive(entry.path) # entry.path 是绝对路径
        except OSError as e:
            print(f"错误: 无法列出目录以进行初始化 {abs_dir_path}: {e}", file=sys.stderr)

    def initialize_protocols(self):
        """
        从基础目录开始，为所有不存在 dirproto.json 文件的子目录初始化空的协议文件。
        建议在加载协议之前调用此方法。
        """
        print(f"\n--- 开始在 '{self.base_dir}' 中进行协议文件初始化 ---")
        if os.path.isdir(self.base_dir): # 确保基础目录存在
            self.initialize_protocols_recursive(self.base_dir)
        else:
            print(f"错误: 无法初始化，因为基础目录 '{self.base_dir}' 不存在或不是目录。", file=sys.stderr)
        print("--- 协议文件初始化完成 ---")

    # --- 协议加载 ---
    def load_protocol_recursive(self, dir_path):
        """
        递归地加载指定目录及其子目录的协议文件，并处理继承。
        (私有辅助方法，通常由 load_protocols 调用)
        """
        abs_dir_path = os.path.abspath(dir_path)

        # 避免重复加载或处理非基础目录下的路径
        if abs_dir_path in self.protocols or not abs_dir_path.startswith(self.base_dir):
            return

        proto_path = os.path.join(abs_dir_path, "dirproto.json")
        proto = {}

        if os.path.exists(proto_path) and os.path.isfile(proto_path):
            try:
                with open(proto_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        proto = json.loads(content)
                        # print(f"已从 {proto_path} 加载协议") # 调试信息
                    # else: # 空文件加载为空协议 {}
                    #    print(f"协议文件为空: {proto_path}") # 调试信息
            except json.JSONDecodeError as e:
                print(f"错误: {proto_path} 中的 JSON 无效: {e}。将使用空协议。", file=sys.stderr)
                proto = {} # 出错时使用空协议
            except OSError as e:
                print(f"错误: 无法读取 {proto_path}: {e}。将使用空协议。", file=sys.stderr)
                proto = {} # 出错时使用空协议
            except Exception as e:
                 print(f"错误: 读取 {proto_path} 时发生意外错误: {e}。将使用空协议。", file=sys.stderr)
                 proto = {}
        else:
             # 如果文件不存在（可能在初始化后被删除），则使用空协议
             # print(f"警告: 协议文件未找到: {proto_path}。将使用空协议。", file=sys.stderr) # 调试信息
             proto = {}

        # --- 处理继承 ---
        if proto.get("inherit_parent", False) and abs_dir_path != self.base_dir:
            parent_dir = os.path.dirname(abs_dir_path)
            # 确保父协议已加载 (递归顺序保证)
            if parent_dir not in self.protocols and parent_dir.startswith(self.base_dir):
                 self.load_protocol_recursive(parent_dir) # 确保父级已加载
            parent_proto = self.protocols.get(parent_dir, {})
            if parent_proto:
                 # print(f"为 {abs_dir_path} 继承自 {parent_dir} 的协议") # 调试信息
                 proto = self.merge_protocol(parent_proto, proto)

        # 存储当前目录最终生效的协议
        self.protocols[abs_dir_path] = proto
        # --- 继承处理结束 ---

        # --- 递归进入子目录 ---
        try:
            for entry in os.scandir(abs_dir_path):
                if entry.is_dir():
                    # 递归加载子目录协议
                    self.load_protocol_recursive(entry.path)
        except OSError as e:
            print(f"错误: 无法列出目录以加载子协议 {abs_dir_path}: {e}", file=sys.stderr)
        # --- 递归结束 ---

    def load_protocols(self):
        """
        加载基础目录下所有子目录的协议文件。
        """
        print(f"\n--- 开始从 '{self.base_dir}' 加载协议 ---")
        self.protocols = {} # 清空旧协议，重新加载
        if os.path.isdir(self.base_dir):
            self.load_protocol_recursive(self.base_dir)
        else:
            print(f"错误: 无法加载协议，因为基础目录 '{self.base_dir}' 不存在或不是目录。", file=sys.stderr)
        print("--- 协议加载完成 ---")


    def merge_protocol(self, parent, child):
        """
        合并父协议和子协议。子协议的键值会覆盖父协议的同名键值。
        注意：对于列表（如 visible_files），子列表会完全替换父列表。
        """
        merged = parent.copy()
        merged.update(child)
        # 如果需要合并列表而不是替换，需要更复杂的逻辑
        # 例如: merged['visible_files'] = list(set(parent.get('visible_files', []) + child.get('visible_files', [])))
        return merged

    # --- 协议查询与检查 ---
    def get_protocol(self, item_path):
        """
        获取指定文件或目录路径 *所在目录* 的有效协议。
        如果目录本身没有协议，则查找父目录，直到找到协议或到达根目录。
        """
        abs_item_path = os.path.abspath(item_path)
        # 获取项目所在的目录路径
        if os.path.isdir(abs_item_path):
            dir_path = abs_item_path
        else:
            dir_path = os.path.dirname(abs_item_path)

        # 向上查找协议直到找到或到达 base_dir 之上
        current_dir = dir_path
        while current_dir.startswith(self.base_dir) or current_dir == self.base_dir:
            # 检查当前目录的协议是否已加载
            proto = self.protocols.get(current_dir)
            if proto is not None: # 找到协议
                # print(f"找到路径 {item_path} 的协议于 {current_dir}") # 调试信息
                return proto

            # 如果已到达 base_dir 且未找到（理论上已加载，除非出错）
            if current_dir == self.base_dir:
                break

            # 移动到父目录
            parent = os.path.dirname(current_dir)
            # 防止无限循环（如果 dirname 不变）
            if parent == current_dir:
                 break
            current_dir = parent

        # print(f"未找到路径 {item_path} 的特定协议，返回空协议") # 调试信息
        return {} # 如果完全找不到协议，返回空

    def is_visible(self, item_path):
        """
        检查一个文件或目录是否在其 *父目录* 的协议中被标记为可见。
        """
        abs_item_path = os.path.abspath(item_path)
        parent_dir_path = os.path.dirname(abs_item_path)
        item_name = os.path.basename(abs_item_path)

        # 如果项目是 base_dir 本身，它总是可见的根
        if abs_item_path == self.base_dir:
            return True

        # 如果父目录在 base_dir 之外，不可见
        if not parent_dir_path.startswith(self.base_dir) and parent_dir_path != self.base_dir:
            return False

        # 获取父目录应用的协议
        parent_proto = self.get_protocol(parent_dir_path) # 直接传递父目录路径

        # print(f"检查 {item_name} 在 {parent_dir_path} 的可见性, 协议 visible_files: {parent_proto.get('visible_files', [])}") # 调试信息
        return item_name in parent_proto.get("visible_files", [])

    def is_operable(self, file_path):
        """
        检查一个文件是否在其 *所在目录* 的协议中被标记为可操作。
        """
        abs_file_path = os.path.abspath(file_path)
        # 获取文件所在目录的协议
        proto = self.get_protocol(abs_file_path) # 传递文件路径以获取其目录协议
        file_name = os.path.basename(abs_file_path)
        # print(f"检查 {file_name} 在 {os.path.dirname(abs_file_path)} 的可操作性, 协议 operable_files: {proto.get('operable_files', [])}") # 调试信息
        return file_name in proto.get("operable_files", [])

    # --- 辅助函数 ---
    def _get_abs_path(self, relative_path):
        """
        辅助函数：将相对于 base_dir 的路径转换为绝对路径。
        """
        # 清理相对路径 (例如, 移除开头的 '/', 处理 '..')
        clean_relative_path = os.path.normpath(relative_path.lstrip(os.path.sep))
        # 防止路径逃逸出 base_dir (基本安全措施)
        abs_path = os.path.join(self.base_dir, clean_relative_path)
        if not os.path.abspath(abs_path).startswith(self.base_dir):
            # 如果计算出的路径不在 base_dir 内，可能是恶意输入或错误
            print(f"警告: 尝试访问基础目录之外的路径 '{relative_path}' -> '{abs_path}'", file=sys.stderr)
            # 可以选择返回 None 或抛出异常
            return None # 或者 raise ValueError("不允许访问基础目录之外的路径")
        return abs_path

    # --- 命令执行 ---
    def execute_command(self, command):
        """
        解析并根据目录协议执行文件操作命令。

        支持的命令格式:
        - "源文件/目录 -> 目标文件/目录"  (移动)
        - "文件 ×"                      (删除)
        - "文件 += \"内容\""            (追加内容)
        - "文件 = \"内容\""             (覆盖内容)
        """
        print(f"执行指令: {command}")
        command = command.strip()

        try:
            # --- 移动操作 ---
            if "->" in command:
                src_rel, dest_rel = map(str.strip, command.split("->", 1))
                src_path = self._get_abs_path(src_rel)
                dest_path = self._get_abs_path(dest_rel)

                if src_path is None or dest_path is None: return # 路径无效或在 base_dir 外
                if not os.path.exists(src_path): print(f"错误: 源 '{src_rel}' 不存在"); return

                if self.is_operable(src_path): # 检查源文件是否可操作
                    try:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True) # 确保目标目录存在
                        shutil.move(src_path, dest_path)
                        print(f"已移动: '{src_rel}' -> '{dest_rel}'")
                        # 注意: 移动操作可能会改变文件的协议环境，但这里不自动重新加载协议
                    except OSError as e: print(f"移动错误: '{src_rel}' -> '{dest_rel}': {e}", file=sys.stderr)
                else: print(f"无权限操作源: '{src_rel}'")

            # --- 删除操作 ---
            elif command.endswith("×"):
                file_rel = command[:-1].strip()
                file_path = self._get_abs_path(file_rel)

                if file_path is None: return # 路径无效
                if not os.path.exists(file_path): print(f"错误: 文件 '{file_rel}' 不存在"); return
                if not os.path.isfile(file_path): print(f"错误: '{file_rel}' 不是一个文件"); return

                if self.is_operable(file_path):
                    try:
                        os.remove(file_path)
                        print(f"已删除: '{file_rel}'")
                    except OSError as e: print(f"删除错误: '{file_rel}': {e}", file=sys.stderr)
                else: print(f"无权限删除: '{file_rel}'")

            # --- 追加操作 ---
            elif "+=" in command:
                parts = command.split("+=", 1)
                if len(parts) == 2:
                    file_rel, content = map(str.strip, parts)
                    content = content.strip('"') # 移除内容两端的引号
                    file_path = self._get_abs_path(file_rel)

                    if file_path is None: return # 路径无效

                    # 检查目标文件路径（即使不存在）是否可操作
                    if self.is_operable(file_path):
                        try:
                            os.makedirs(os.path.dirname(file_path), exist_ok=True) # 确保目录存在
                            with open(file_path, "a", encoding='utf-8') as f:
                                f.write(content + "\n")
                            print(f"已追加内容到 '{file_rel}'")
                        except OSError as e: print(f"追加错误: '{file_rel}': {e}", file=sys.stderr)
                    else:
                        # 提供更具体的无权限信息
                        if os.path.exists(file_path): print(f"无权限编辑: '{file_rel}'")
                        else: print(f"无权限创建或编辑: '{file_rel}'")
                else: print(f"格式错误 (+=): '{command}'", file=sys.stderr)

            # --- 覆盖操作 ---
            elif "=" in command:
                parts = command.split("=", 1)
                if len(parts) == 2:
                    file_rel, content = map(str.strip, parts)
                    content = content.strip('"') # 移除内容两端的引号
                    file_path = self._get_abs_path(file_rel)

                    if file_path is None: return # 路径无效

                    if self.is_operable(file_path):
                         try:
                            os.makedirs(os.path.dirname(file_path), exist_ok=True) # 确保目录存在
                            with open(file_path, "w", encoding='utf-8') as f:
                                f.write(content + "\n")
                            print(f"已覆盖内容到 '{file_rel}'")
                         except OSError as e: print(f"写入错误: '{file_rel}': {e}", file=sys.stderr)
                    else:
                        if os.path.exists(file_path): print(f"无权限编辑: '{file_rel}'")
                        else: print(f"无权限创建或编辑: '{file_rel}'")
                else: print(f"格式错误 (=): '{command}'", file=sys.stderr)

            # --- 未知命令 ---
            else: print(f"无法识别的指令: '{command}'", file=sys.stderr)

        except Exception as e:
             print(f"处理指令时发生意外错误 '{command}': {e}", file=sys.stderr)
             # 可以选择在这里打印更详细的 traceback
             # import traceback
             # traceback.print_exc()

    # --- 目录树展示 ---
    def display_tree(self):
        """
        以树状结构展示协议中定义为 'visible' 的文件和目录。
        """
        # 确保协议已加载
        if not self.protocols:
            print("协议尚未加载，现在开始加载...")
            self.load_protocols() # 调用公共加载方法
            if not self.protocols:
                print("错误: 协议加载失败，无法展示目录树。", file=sys.stderr)
                return

        print(f"\n--- 可见文件/目录树 ({os.path.basename(self.base_dir)}) ---")
        # 打印根目录名称，根目录总是可见
        print(f"{os.path.basename(self.base_dir)}/")
        # 调用递归辅助函数，从基础目录开始
        if os.path.isdir(self.base_dir):
            self._display_tree_recursive(self.base_dir, "")
        print("--- 树展示完毕 ---")

    def _display_tree_recursive(self, current_dir_abs, prefix):
        """
        递归辅助函数，用于打印树状结构。
        (私有辅助方法)
        """
        try:
            # 使用 scandir 获取目录内容条目列表
            entries = list(os.scandir(current_dir_abs))
        except OSError as e:
            # 如果无法访问目录（例如权限问题），打印错误信息并返回
            print(f"{prefix}└── [错误: 无法访问目录 '{os.path.basename(current_dir_abs)}': {e}]", file=sys.stderr)
            return

        # 过滤出可见的项目 (检查 item 在其父目录协议中的可见性)
        visible_entries = sorted(
            [entry for entry in entries if self.is_visible(entry.path)],
            key=lambda e: (not e.is_dir(), e.name.lower()) # 目录优先，然后按名称排序
        )

        # 遍历可见项目
        num_visible = len(visible_entries)
        for i, entry in enumerate(visible_entries):
            # 判断是否是当前目录下的最后一个可见项目
            is_last = (i == num_visible - 1)
            # 根据是否最后一个项目选择连接符
            connector = "└── " if is_last else "├── "

            # 打印当前项目行
            print(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")

            # 如果当前项目是目录，并且它本身也是可见的（上面已检查过），则递归进入
            if entry.is_dir():
                # 计算下一层递归的前缀
                # 如果当前是最后一个，则下一层前缀使用空格缩进
                # 否则，使用竖线 | 连接符表示下方还有同级项目
                new_prefix = prefix + ("    " if is_last else "│   ")
                # 递归调用
                self._display_tree_recursive(entry.path, new_prefix)


# --- 测试环境设置与执行 ---
def setup_test_environment(base):
    """创建用于测试的临时目录结构和示例协议文件。"""
    base = os.path.abspath(base) # 确保 base 是绝对路径
    print(f"\n--- 正在设置测试环境于: {base} ---")
    if os.path.exists(base):
        print(f"警告: 测试目录已存在，将先删除: {base}")
        shutil.rmtree(base)
    try:
        # 创建目录结构
        os.makedirs(base)
        os.makedirs(os.path.join(base, "src"))
        os.makedirs(os.path.join(base, "docs"))
        os.makedirs(os.path.join(base, "tests"))
        os.makedirs(os.path.join(base, "data", "raw")) # 嵌套子目录
        os.makedirs(os.path.join(base, "hidden_dir"))

        # 创建示例文件
        with open(os.path.join(base, "README.md"), "w", encoding='utf-8') as f: f.write("# 项目说明\n")
        with open(os.path.join(base, "main.py"), "w", encoding='utf-8') as f: f.write("print('Hello main')\n")
        with open(os.path.join(base, ".gitignore"), "w", encoding='utf-8') as f: f.write("*.pyc\n")
        with open(os.path.join(base, "src", "module.py"), "w", encoding='utf-8') as f: f.write("def func(): pass\n")
        with open(os.path.join(base, "src", "config.json"), "w", encoding='utf-8') as f: f.write('{"key": "value"}\n')
        with open(os.path.join(base, "docs", "index.html"), "w", encoding='utf-8') as f: f.write("<h1>Docs</h1>\n")
        with open(os.path.join(base, "data", "raw", "data1.csv"), "w", encoding='utf-8') as f: f.write("col1,col2\n1,2\n")
        with open(os.path.join(base, "tests", "test_main.py"), "w", encoding='utf-8') as f: f.write("assert True\n")
        with open(os.path.join(base, "hidden_dir", "secret.txt"), "w", encoding='utf-8') as f: f.write("Secret content\n")


        # --- 创建协议文件 ---
        # 根目录协议
        base_proto = {
            # inherit_parent: False (默认)
            "visible_files": ["README.md", "main.py", "src", "docs", "data", "tests"], # .gitignore 和 hidden_dir 不可见
            "operable_files": ["README.md", "main.py"] # 只有这两个文件在根目录可操作
        }
        with open(os.path.join(base, "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(base_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'dirproto.json')}")

        # src 目录协议 (继承并添加)
        src_proto = {
            "inherit_parent": True,
            "visible_files": ["module.py", "config.json"], # 明确定义 src 下可见内容 (会替换父级列表)
            "operable_files": ["module.py", "config.json"] # 允许操作 src 下的文件
        }
        # 注意: 由于 merge_protocol 默认是替换列表，如果想"添加"到父级可见/可操作列表，需要修改 merge_protocol 或在这里写完整列表
        # 如果 merge_protocol 是替换:
        # src_proto_merged_visible = base_proto['visible_files'] + ["module.py", "config.json"] # 假设想要合并
        # src_proto['visible_files'] = list(set(src_proto_merged_visible)) # 合并并去重
        # 但当前实现是替换，所以上面定义的 src_proto 即可

        with open(os.path.join(base, "src", "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(src_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'src', 'dirproto.json')}")

        # data 目录协议 (仅定义可操作，不继承，可见性为空，则子目录也不可见)
        data_proto = {
            "inherit_parent": False,
            "visible_files": ["raw"], # 只让 raw 子目录可见
            "operable_files": [] # data 目录本身及文件不可操作
        }
        with open(os.path.join(base, "data", "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(data_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'data', 'dirproto.json')}")

        # data/raw 目录协议 (允许操作 csv)
        data_raw_proto = {
             "inherit_parent": False, # 不继承自空的 data 协议
             "visible_files": ["data1.csv"],
             "operable_files": ["data1.csv"]
        }
        with open(os.path.join(base, "data", "raw", "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(data_raw_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'data', 'raw', 'dirproto.json')}")


        # docs 和 tests 目录将使用 initialize_protocols 创建空的 {} 协议

        print("--- 测试环境设置完毕 ---")

    except Exception as e:
        print(f"设置测试环境时出错: {e}", file=sys.stderr)
        # 在出错时尝试清理，避免留下部分创建的目录
        if os.path.exists(base):
             print(f"尝试清理未完成的测试环境: {base}")
             shutil.rmtree(base)
        raise # 重新抛出异常，让调用者知道设置失败

if __name__ == "__main__":
    TEST_DIR_NAME = "project_proto_test"
    # 在脚本所在目录下创建测试目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    TEST_DIR = os.path.join(script_dir, TEST_DIR_NAME)

    try:
        # 1. 设置测试环境
        # setup_test_environment(TEST_DIR)

        # 2. 初始化管理器
        print("\n--- 步骤 2: 初始化 DirProtoManager ---")
        manager = DirProtoManager(TEST_DIR)

        # 3. 初始化协议文件 (确保所有目录都有 dirproto.json)
        print("\n--- 步骤 3: 初始化协议文件 ---")
        manager.initialize_protocols()

        # 4. 加载所有协议
        print("\n--- 步骤 4: 加载协议 ---")
        manager.load_protocols()

        # 5. 展示初始的可见目录树
        print("\n--- 步骤 5: 展示初始可见目录树 ---")
        manager.display_tree()

        # 6. 执行一些命令
        print("\n--- 步骤 6: 执行命令 ---")
        # 成功操作 (根目录下可操作)
        manager.execute_command("README.md += \"\\n## 更新说明\\n这是新增的内容。\"")
        manager.execute_command("README.md ×")
        # 失败操作 (根目录下不可操作)
        manager.execute_command(".gitignore ×")
        # 失败操作 (访问隐藏目录下的文件，父目录不可见导致路径解析失败或权限检查失败)
        manager.execute_command("hidden_dir/secret.txt = \"New secret\"")
        # 成功操作 (src 下可操作)
        manager.execute_command("src/module.py = \"# Rewritten module\\ndef new_func(): return 1\"")
        # 失败操作 (src 下 config.json 可见可操作，但尝试移到不可操作的 data 目录)
        # 移动只需要源可操作，目标目录存在即可
        manager.execute_command("src/config.json -> data/config_moved.json")
        # 成功操作 (data/raw 下可操作)
        manager.execute_command("data/raw/data1.csv += \"12354\\n\"")
        # 失败操作 (docs 目录使用空协议，不可操作)
        manager.execute_command("docs/index.html ×")
        # 移动到 tests 目录 (tests 使用空协议，但移动只检查源权限)
        manager.execute_command("main.py -> tests/main_moved.py")


        # 7. 再次展示目录树，查看变化
        print("\n--- 步骤 7: 展示操作后的可见目录树 ---")
        manager.display_tree()

        # 8. 检查文件内容变化 (可选)
        print("\n--- 步骤 8: 检查文件内容 (可选) ---")
        readme_path = os.path.join(TEST_DIR, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                print(f"README.md 内容片段:\n{f.read()[-50:]}...") # 只显示最后一部分

        dataraw_path = os.path.join(TEST_DIR, "data", "raw", "data1.csv")
        if os.path.exists(dataraw_path):
            with open(dataraw_path, 'r', encoding='utf-8') as f:
                print(f"data1.csv 内容:\n{f.read()}")

    except Exception as main_e:
        print(f"\n主程序执行过程中发生错误: {main_e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

    finally:
        # 清理测试环境
        cleanup = input(f"\n是否清理测试目录 '{TEST_DIR}'? (y/N): ")
        if cleanup.lower() == 'y':
            try:
                print(f"--- 清理测试目录 {TEST_DIR} ---")
                shutil.rmtree(TEST_DIR)
                print("清理完成。")
            except OSError as clean_e:
                print(f"清理测试目录时出错: {clean_e}", file=sys.stderr)
        else:
            print(f"保留测试目录: {TEST_DIR}")