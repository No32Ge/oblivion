import os
import json
import shutil
import sys
import errno # Import errno for specific error checking

class DirProtoManager:
    """
    管理基于目录协议 (dirproto.json) 的文件操作和可见性。

    协议文件 (dirproto.json) 结构示例:
    {
        "inherit_parent": true,  # 是否继承父目录协议 (默认为 false)
        "visible_files": ["file1.txt", "subdir", "script.py"], # 在此目录中可见的文件/子目录列表
        "operable_files": ["file1.txt", "script.py", "<create>"], # 在此目录中可操作 (编辑/删除/移动源) 的文件列表。
                                                               # 特殊值 "<create>" 允许在此目录中创建新文件或子目录。
        "show_content": true # 是否显示此目录中可见文本文件的内容预览 (默认为 false)，主要用于 display_tree
    }
    """
    # Define common text and binary file extensions
    TEXT_EXTENSIONS = (".py", ".js", ".html", ".css", ".md", ".json", ".txt", ".csv", ".xml", ".yml", ".yaml", ".log", ".cfg", ".conf")
    BINARY_EXTENSIONS = (".mp3", ".mp4", ".wav", ".ogg", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".zip", ".tar", ".gz", ". सातz", ".pdf", ".exe", ".dll", ".so", ".bin", ".ico") # More can be added

    def __init__(self, base_dir):
        """
        Initializes the DirProtoManager.
        :param base_dir: The absolute path to the project's root directory.
        """
        # Use absolute path for consistency
        self.base_dir = os.path.abspath(base_dir)
        self.protocols = {} # Stores loaded protocols, keyed by absolute directory path
        print(f"初始化 DirProtoManager，基础目录: {self.base_dir}")
        if not os.path.isdir(self.base_dir):
            print(f"警告: 基础目录 '{self.base_dir}' 不存在或不是一个目录。", file=sys.stderr)
            # Consider raising an exception here if the base directory doesn't exist, as operations would fail.
            # raise FileNotFoundError(f"Base directory '{self.base_dir}' not found or is not a directory")

    # --- Protocol File Initialization ---
    def initialize_protocols_recursive(self, dir_path):
        """
        Recursively ensures dirproto.json files exist in dir_path and all its subdirectories.
        Creates an empty '{}' file if it doesn't exist. Skips if it already exists.
        (Private helper method)
        """
        abs_dir_path = os.path.abspath(dir_path)

        # Security check: Only operate within base_dir
        if os.path.commonpath([abs_dir_path, self.base_dir]) != self.base_dir:
            return

        proto_path = os.path.join(abs_dir_path, "dirproto.json")

        # Check if file exists, create if not
        if not os.path.exists(proto_path):
            try:
                with open(proto_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f) # Write an empty JSON object
                # print(f"Initialized empty protocol file: {proto_path}") # Too verbose
            except OSError as e:
                print(f"错误: 无法创建协议文件 {proto_path}: {e}", file=sys.stderr)
            except Exception as e: # Catch other potential errors
                 print(f"错误: 创建协议文件 {proto_path} 时发生意外错误: {e}", file=sys.stderr)

        # Recursively enter subdirectories
        try:
            for entry in os.scandir(abs_dir_path):
                if entry.is_dir():
                    self.initialize_protocols_recursive(entry.path) # entry.path is already absolute
        except OSError as e:
            print(f"错误: 无法列出目录以进行初始化 {abs_dir_path}: {e}", file=sys.stderr)

    def initialize_protocols(self):
        """
        Starts from the base directory and initializes empty protocol files for all subdirectories where dirproto.json is missing.
        Recommended to call this before loading protocols.
        """
        print(f"\n--- 开始在 '{self.base_dir}' 中进行协议文件初始化 ---")
        if os.path.isdir(self.base_dir): # Ensure base directory exists
            self.initialize_protocols_recursive(self.base_dir)
        else:
            print(f"错误: 无法初始化，因为基础目录 '{self.base_dir}' 不存在或不是目录。", file=sys.stderr)
        print("--- 协议文件初始化完成 ---")

    # --- Protocol Loading ---
    def load_protocol_recursive(self, dir_path):
        """
        Recursively loads protocol files for the specified directory and its subdirectories, handling inheritance.
        Populates self.protocols dictionary.
        """
        abs_dir_path = os.path.abspath(dir_path)

        # Avoid reloading or processing paths outside base_dir
        if abs_dir_path in self.protocols or (os.path.commonpath([abs_dir_path, self.base_dir]) != self.base_dir):
            return

        proto_path = os.path.join(abs_dir_path, "dirproto.json")
        proto = {}

        if os.path.exists(proto_path) and os.path.isfile(proto_path):
            try:
                with open(proto_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        proto = json.loads(content)
                        # print(f"DEBUG_LOAD_RECUR: Loaded protocol from '{os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path}'")
                    # else: print(f"DEBUG_LOAD_RECUR: Protocol file empty: '{os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path}'. Using empty protocol.")

            except json.JSONDecodeError as e:
                print(f"错误: {os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path} 中的 JSON 无效: {e}。将使用空协议。", file=sys.stderr)
                proto = {} # Use empty protocol on error
            except OSError as e:
                print(f"错误: 无法读取 {os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path}: {e}。将使用空协议。", file=sys.stderr)
                proto = {} # Use empty protocol on error
            except Exception as e:
                 print(f"错误: 读取 {os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path} 时发生意外错误: {e}。将使用空协议。", file=sys.stderr)
                 proto = {}
        else:
             # If file doesn't exist (maybe deleted after init), use empty protocol
             # print(f"DEBUG_LOAD_RECUR: Protocol file not found: '{os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path}'. Using empty protocol.") # Debug info
             proto = {}

        # --- Handle Inheritance ---
        if proto.get("inherit_parent", False) and abs_dir_path != self.base_dir:
            parent_dir = os.path.dirname(abs_dir_path)
            if os.path.commonpath([parent_dir, self.base_dir]) == self.base_dir:
                 if parent_dir not in self.protocols:
                     # print(f"DEBUG_LOAD_RECUR: Recursively loading parent protocol for '{os.path.relpath(abs_dir_path, self.base_dir) if os.path.exists(self.base_dir) else abs_dir_path}': '{os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir}'") # Debug
                     self.load_protocol_recursive(parent_dir) # Ensure parent is loaded

                 parent_proto = self.protocols.get(parent_dir, {})
                 if parent_proto:
                      # print(f"DEBUG_LOAD_RECUR: Merging protocol for '{os.path.relpath(abs_dir_path, self.base_dir) if os.path.exists(self.base_dir) else abs_dir_path}' from parent '{os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir}'") # Debug info
                      proto = self.merge_protocol(parent_proto, proto)
            else:
                try:
                     rel_abs_dir = os.path.relpath(abs_dir_path, self.base_dir)
                     rel_parent_dir = os.path.relpath(parent_dir, os.path.dirname(parent_dir)) # Relative to its own parent if outside base
                except ValueError:
                     rel_abs_dir = abs_dir_path
                     rel_parent_dir = parent_dir
                print(f"警告: 路径 '{rel_abs_dir}' 尝试继承其父目录 '{rel_parent_dir}'，但父目录超出基础目录 '{self.base_dir}' 范围，忽略继承。", file=sys.stderr)


        # Store the final effective protocol for the current directory
        self.protocols[abs_dir_path] = proto
        # print(f"DEBUG_LOAD_STORE: Stored protocol for '{os.path.relpath(abs_dir_path, self.base_dir) if os.path.exists(self.base_dir) else abs_dir_path}'. Total keys in protocols: {len(self.protocols)}")


        # --- Recurse into subdirectories ---
        try:
            for entry in os.scandir(abs_dir_path):
                if entry.is_dir():
                    self.load_protocol_recursive(entry.path)
        except OSError as e:
            try:
                 rel_path = os.path.relpath(abs_dir_path, self.base_dir)
            except ValueError:
                 rel_path = abs_dir_path
            print(f"错误: 无法列出目录以加载子协议 {rel_path}: {e}", file=sys.stderr)


    def load_protocols(self):
        """Loads all protocol files under the base directory."""
        print(f"\n--- 开始从 '{self.base_dir}' 加载协议 ---")
        self.protocols = {} # Clear old protocols before reloading
        if os.path.isdir(self.base_dir):
            self.load_protocol_recursive(self.base_dir)
        else:
            print(f"错误: 无法加载协议，因为基础目录 '{self.base_dir}' 不存在或不是目录。", file=sys.stderr)
        print("--- 协议加载完成 ---")


    def merge_protocol(self, parent, child):
        """Merges parent and child protocols. Child values override parent values."""
        merged = parent.copy()
        # Special handling for lists like visible_files and operable_files:
        # The child list completely replaces the parent list if the key exists in the child.
        # This logic is handled by dict.update() itself for top-level keys.
        merged.update(child)
        return merged


    # --- Protocol Lookup and Checks ---
    def get_protocol(self, item_path):
        """
        Gets the effective protocol for the directory containing the specified file or directory path.
        Traverses up from the item's directory until a protocol is found or the base directory is reached.
        """
        abs_item_path = os.path.abspath(item_path)
        if os.path.isdir(abs_item_path):
            dir_path = abs_item_path
        else:
            dir_path = os.path.dirname(abs_item_path)

        current_dir = dir_path
        while os.path.commonpath([current_dir, self.base_dir]) == self.base_dir:
            # Uncomment for deep debug
            # try: rel_current_dir = os.path.relpath(current_dir, self.base_dir)
            # except ValueError: rel_current_dir = current_dir
            # print(f"DEBUG_GET_PROTOCOL:   Checking '{current_dir}' (relative: '{rel_current_dir}') in self.protocols. Keys present count: {len(self.protocols)}.") # Debug

            proto = self.protocols.get(current_dir)
            if proto is not None:
                # print(f"DEBUG_GET_PROTOCOL:   Found protocol for '{current_dir}'") # Debug
                return proto

            if current_dir == self.base_dir:
                # print(f"DEBUG_GET_PROTOCOL: Reached base_dir '{self.base_dir}', stopping traversal.") # Debug
                break

            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                 # print(f"DEBUG_GET_PROTOCOL: Reached file system root from '{current_dir}', stopping traversal.") # Debug
                 break
            current_dir = parent

        # print(f"DEBUG_GET_PROTOCOL: Traversal ended for '{os.path.relpath(abs_item_path, self.base_dir) if os.path.exists(abs_item_path) else abs_item_path}'. No protocol found up to base_dir.") # Debug
        return {} # Return empty protocol if none found in hierarchy


    def is_visible(self, item_path):
        """Checks if an item is marked as visible in its parent directory's protocol."""
        abs_item_path = os.path.abspath(item_path)
        parent_dir_path = os.path.dirname(abs_item_path)
        item_name = os.path.basename(abs_item_path)

        if abs_item_path == self.base_dir: return True # Base dir is always visible root

        if os.path.commonpath([parent_dir_path, self.base_dir]) != self.base_dir:
             # print(f"DEBUG_VISIBLE: Item='{item_name}', Parent='{parent_dir_path}'. Parent outside base_dir '{self.base_dir}'. Invisible.") # Debug
             return False

        parent_proto = self.get_protocol(parent_dir_path)
        visible_list = parent_proto.get("visible_files", [])
        is_item_visible = item_name in visible_list

        # Uncomment for deep debug
        # try: rel_parent_dir_path = os.path.relpath(parent_dir_path, self.base_dir)
        # except ValueError: rel_parent_dir_path = parent_dir_path
        # print(f"DEBUG_VISIBLE: Item='{item_name}', Parent='{rel_parent_dir_path}', VisibleList={visible_list}, IsVisible={is_item_visible}") # Debug

        return is_item_visible


    def is_operable(self, item_path):
        """
        Checks if a file is marked as operable in its containing directory's protocol.
        Note: Directories are not considered operable by this method (use '<create>' for dir creation).
        """
        abs_item_path = os.path.abspath(item_path)
        if not os.path.isfile(abs_item_path):
             return False # Only files are operable for modification/deletion

        proto = self.get_protocol(abs_item_path) # Gets protocol of containing directory
        item_name = os.path.basename(abs_item_path)
        operable_list = proto.get("operable_files", [])
        is_item_operable = item_name in operable_list

        # Uncomment for deep debug
        # try: rel_dir_path = os.path.relpath(os.path.dirname(abs_item_path), self.base_dir)
        # except ValueError: rel_dir_path = os.path.dirname(abs_item_path)
        # print(f"DEBUG_OPERABLE: Item='{item_name}', Dir='{rel_dir_path}', OperableList={operable_list}, IsOperable={is_item_operable}") # Debug

        return is_item_operable


    def can_create_in_dir(self, target_dir_path):
        """Checks if creation is allowed within the specified target directory based on its protocol."""
        abs_target_dir_path = os.path.abspath(target_dir_path)

        # Ensure target directory is within base_dir
        if os.path.commonpath([abs_target_dir_path, self.base_dir]) != self.base_dir:
            # print(f"DEBUG_CAN_CREATE: Target dir '{abs_target_dir_path}' outside base_dir. Cannot create.") # Debug
            return False

        # Get the protocol *for* the target directory itself
        target_proto = self.get_protocol(abs_target_dir_path)
        operable_list = target_proto.get("operable_files", [])
        can_create = "<create>" in operable_list

        # Uncomment for deep debug
        # try: rel_target_dir = os.path.relpath(abs_target_dir_path, self.base_dir)
        # except ValueError: rel_target_dir = abs_target_dir_path
        # print(f"DEBUG_CAN_CREATE: TargetDir='{rel_target_dir}', OperableList={operable_list}, CanCreate={can_create}") # Debug

        return can_create


    def should_show_content_preview(self, file_path):
        """Checks if a text file's content preview should be shown based on its directory's protocol."""
        abs_file_path = os.path.abspath(file_path)
        if not os.path.isfile(abs_file_path): return False

        ext = os.path.splitext(abs_file_path)[1].lower()
        if ext not in self.TEXT_EXTENSIONS: return False

        proto = self.get_protocol(abs_file_path)
        return proto.get("show_content", False)

    # --- Auxiliary Function ---
    def _get_abs_path(self, relative_path):
        """
        Converts a path relative to base_dir to an absolute path.
        Performs security check to ensure the path stays within base_dir.
        Returns absolute path or None if outside base_dir or invalid.
        """
        try:
            # Join with base_dir first
            full_path = os.path.join(self.base_dir, relative_path)
            # Normalize and make absolute (resolves '..')
            abs_path = os.path.normpath(os.path.abspath(full_path))

            # Security check: Use commonpath
            if os.path.commonpath([abs_path, self.base_dir]) == self.base_dir:
                 return abs_path
            else:
                print(f"警告: 尝试访问基础目录之外的路径 '{relative_path}' -> '{abs_path}' (计算结果超出: '{self.base_dir}')", file=sys.stderr)
                return None
        except Exception as e: # Catch potential errors during path manipulation
             print(f"错误: 处理路径时出错 '{relative_path}': {e}", file=sys.stderr)
             return None


    # --- File Content Reading ---
    def read_file_content(self, file_path):
        """
        Reads the full content of a visible file.
        Returns string content for text files, identifier for binary files.
        Returns None on error, non-existence, non-visibility, or invalid path.
        """
        abs_file_path = self._get_abs_path(file_path)
        if abs_file_path is None: return None # Outside base or invalid

        if not os.path.exists(abs_file_path):
             print(f"错误: 文件不存在: '{file_path}'", file=sys.stderr); return None
        if not os.path.isfile(abs_file_path):
             print(f"错误: 路径不是一个文件: '{file_path}'", file=sys.stderr); return None
        if not self.is_visible(abs_file_path):
             print(f"错误: 文件 '{file_path}' 根据协议不可见，无法读取内容。", file=sys.stderr); return None

        ext = os.path.splitext(abs_file_path)[1].lower()
        if ext in self.BINARY_EXTENSIONS:
            print(f"警告: 尝试读取二进制文件内容: '{file_path}'", file=sys.stderr)
            return "[这是一个二进制文件，不显示其内容]"
        elif ext in self.TEXT_EXTENSIONS:
            try:
                with open(abs_file_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            except Exception as e:
                print(f"错误: 读取文件 '{file_path}' 失败: {e}", file=sys.stderr)
                return f"[读取文件失败: {e}]"
        else:
             print(f"警告: 尝试读取未知文件类型内容: '{file_path}'", file=sys.stderr)
             return "[未知类型文件，不显示内容]"


    # --- Command Execution ---
    def execute_command(self, command):
        """
        Parses and executes file operation commands based on directory protocols.

        Supported command formats:
        - "source_file/dir -> dest_file/dir" (Move/Rename)
        - "item ×"                           (Delete file/dir)
        - "file += \"content\""              (Append content to file)
        - "file = \"content\""               (Overwrite content to file)
        - "touch path/to/new_file.txt"       (Create empty file)
        - "mkdir path/to/new_dir"            (Create directory)
        """
        print(f"\n执行指令: {command}")
        command = command.strip()

        try:
            # --- Move Operation ---
            if "->" in command:
                parts = command.split("->", 1)
                if len(parts) != 2: print(f"格式错误 (->): '{command}'", file=sys.stderr); return
                src_rel, dest_rel = map(str.strip, parts)
                src_path = self._get_abs_path(src_rel)
                dest_path = self._get_abs_path(dest_rel)

                if src_path is None or dest_path is None: return
                if not os.path.exists(src_path): print(f"错误: 源 '{src_rel}' 不存在"); return

                # Check source operability if it's a file
                if os.path.isfile(src_path) and not self.is_operable(src_path):
                     print(f"无权限操作源文件: '{src_rel}'"); return
                # Check creation permission in destination directory if destination doesn't exist
                # (Move implicitly creates if target name is new)
                dest_parent_dir = os.path.dirname(dest_path)
                if not os.path.exists(dest_path) and not self.can_create_in_dir(dest_parent_dir):
                    rel_dest_parent = os.path.relpath(dest_parent_dir, self.base_dir) if os.path.exists(self.base_dir) else dest_parent_dir
                    print(f"无权限在目录 '{rel_dest_parent}' 中创建目标 '{os.path.basename(dest_path)}'"); return

                try:
                    dest_parent_dir = os.path.dirname(dest_path)
                    if os.path.commonpath([dest_parent_dir, self.base_dir]) != self.base_dir:
                         print(f"错误: 目标目录 '{dest_rel}' 超出基础目录范围。", file=sys.stderr); return
                    os.makedirs(dest_parent_dir, exist_ok=True) # Ensure parent exists

                    shutil.move(src_path, dest_path)
                    print(f"已移动: '{src_rel}' -> '{dest_rel}'")
                except OSError as e: print(f"移动错误: '{src_rel}' -> '{dest_rel}': {e}", file=sys.stderr)
                except Exception as e: print(f"移动 '{src_rel}' -> '{dest_rel}' 时发生意外错误: {e}", file=sys.stderr)

            # --- Delete Operation ---
            elif command.endswith("×"):
                item_rel = command[:-1].strip()
                item_path = self._get_abs_path(item_rel)

                if item_path is None: return
                if not os.path.exists(item_path): print(f"错误: 项目 '{item_rel}' 不存在"); return

                # Check operability if it's a file
                if os.path.isfile(item_path) and not self.is_operable(item_path):
                     print(f"无权限删除文件: '{item_rel}'"); return
                # Check creation permission in parent dir for directories? No, deletion is different.
                # Let's assume if a dir is visible (controlled by parent) and within base_dir, it can be deleted.

                try:
                    if os.path.isfile(item_path):
                         os.remove(item_path)
                         print(f"已删除文件: '{item_rel}'")
                    elif os.path.isdir(item_path):
                         shutil.rmtree(item_path)
                         print(f"已删除目录: '{item_rel}'")
                    else: print(f"警告: 无法删除特殊文件类型 '{item_rel}'", file=sys.stderr)
                except OSError as e: print(f"删除错误: '{item_rel}': {e}", file=sys.stderr)
                except Exception as e: print(f"删除 '{item_rel}' 时发生意外错误: {e}", file=sys.stderr)

            # --- Append or Overwrite Operation ---
            elif "+=" in command or "=" in command:
                operator = "+=" if "+=" in command else "="
                parts = command.split(operator, 1)
                if len(parts) == 2:
                    file_rel, content_part = map(str.strip, parts)
                    content = content_part
                    if content.startswith('"') and content.endswith('"'): content = content[1:-1].replace('\\n', '\n').replace('\\"', '"')
                    elif content.startswith("'") and content.endswith("'"): content = content[1:-1].replace('\\n', '\n').replace("\\'", "'")

                    file_path = self._get_abs_path(file_rel)
                    if file_path is None: return
                    if os.path.isdir(file_path): print(f"错误: 无法向目录 '{file_rel}' 写入内容。", file=sys.stderr); return

                    # Check operability OR creation permission if file doesn't exist
                    parent_dir = os.path.dirname(file_path)
                    can_operate = False
                    if os.path.exists(file_path):
                        # File exists, check standard operability
                        can_operate = self.is_operable(file_path)
                        if not can_operate: print(f"无权限编辑文件: '{file_rel}'")
                    else:
                        # File doesn't exist, check creation permission in parent directory
                        can_operate = self.can_create_in_dir(parent_dir)
                        if not can_operate:
                            rel_parent = os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir
                            print(f"无权限在目录 '{rel_parent}' 中创建文件 '{os.path.basename(file_path)}'")


                    if can_operate:
                        try:
                            if os.path.commonpath([parent_dir, self.base_dir]) != self.base_dir:
                                 print(f"错误: 目标文件父目录 '{os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir}' 超出基础目录范围。", file=sys.stderr)
                                 return
                            os.makedirs(parent_dir, exist_ok=True) # Ensure parent exists

                            mode = "a" if operator == "+=" else "w"
                            ext = os.path.splitext(file_path)[1].lower()
                            if os.path.exists(file_path) and ext not in self.TEXT_EXTENSIONS:
                                print(f"错误: 无法使用文本内容操作符 ({operator}) 修改非文本文件 '{file_rel}'", file=sys.stderr)
                                return

                            with open(file_path, mode, encoding='utf-8') as f: f.write(content)
                            print(f"已使用 '{operator}' 更新/创建文件 '{file_rel}'")
                        except OSError as e: print(f"文件写入错误 ({operator}): '{file_rel}': {e}", file=sys.stderr)
                        except Exception as e: print(f"更新文件 '{file_rel}' 时发生意外错误: {e}", file=sys.stderr)
                    # else: Permission error message already printed above

                else: print(f"格式错误 ({operator}): '{command}'", file=sys.stderr)

            # --- Create Empty File Operation ---
            elif command.startswith("touch "):
                item_rel = command[len("touch "):].strip()
                item_path = self._get_abs_path(item_rel)
                if item_path is None: return

                if os.path.exists(item_path):
                    print(f"错误: '{item_rel}' 已存在，无法创建。")
                    return

                parent_dir = os.path.dirname(item_path)
                if not self.can_create_in_dir(parent_dir):
                    rel_parent = os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir
                    print(f"无权限在目录 '{rel_parent}' 中创建文件。")
                    return

                try:
                    os.makedirs(parent_dir, exist_ok=True) # Ensure parent directory exists
                    with open(item_path, 'w', encoding='utf-8') as f: pass # Create empty file
                    print(f"已创建空文件: '{item_rel}'")
                except OSError as e: print(f"创建文件错误 '{item_rel}': {e}", file=sys.stderr)
                except Exception as e: print(f"创建文件 '{item_rel}' 时发生意外错误: {e}", file=sys.stderr)

            # --- Create Directory Operation ---
            elif command.startswith("mkdir "):
                dir_rel = command[len("mkdir "):].strip()
                dir_path = self._get_abs_path(dir_rel)
                if dir_path is None: return

                if os.path.exists(dir_path):
                    print(f"错误: '{dir_rel}' 已存在，无法创建。")
                    return

                parent_dir = os.path.dirname(dir_path)
                 # Need to check creation permission in the *parent* of the directory being created
                if not self.can_create_in_dir(parent_dir):
                    rel_parent = os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir
                    print(f"无权限在目录 '{rel_parent}' 中创建目录。")
                    return

                try:
                    os.makedirs(dir_path) # Creates the directory; fails if it exists
                    print(f"已创建目录: '{dir_rel}'")
                    # Initialize an empty dirproto.json in the new directory
                    proto_path = os.path.join(dir_path, "dirproto.json")
                    try:
                        with open(proto_path, 'w', encoding='utf-8') as f: json.dump({}, f)
                        print(f"已在 '{dir_rel}' 中初始化空的 dirproto.json")
                        # Add the new protocol to our loaded protocols immediately?
                        # Or rely on reload? Let's add it immediately for consistency.
                        self.protocols[dir_path] = {} # Store empty protocol
                    except OSError as e_proto: print(f"警告: 无法在新建目录 '{dir_rel}' 中创建 dirproto.json: {e_proto}", file=sys.stderr)

                except OSError as e:
                    # Check specifically for FileExistsError (errno 17)
                    if e.errno == errno.EEXIST: print(f"错误: '{dir_rel}' 已存在，无法创建。")
                    else: print(f"创建目录错误 '{dir_rel}': {e}", file=sys.stderr)
                except Exception as e: print(f"创建目录 '{dir_rel}' 时发生意外错误: {e}", file=sys.stderr)

            # --- Unknown Command ---
            else: print(f"无法识别的指令: '{command}'", file=sys.stderr)

        except Exception as e:
             print(f"处理指令时发生意外错误 '{command}': {e}", file=sys.stderr)
             import traceback
             traceback.print_exc() # Print full traceback for unexpected errors


    # --- Directory Tree Display ---
    def display_tree(self, show_lines=None):
        """
        Displays visible files and directories in a tree structure according to the protocol.
        Optional parameter show_lines: Limits lines shown for visible text file content preview.
        """
        if not self.protocols:
            print("协议尚未加载，现在开始加载...")
            self.load_protocols()
            if not self.protocols:
                print("错误: 协议加载失败，无法展示目录树。", file=sys.stderr); return

        print(f"\n--- 可见文件/目录树 ({os.path.basename(self.base_dir)}) ---")
        tree_data = self._build_visible_tree_recursive(self.base_dir)
        if tree_data is not None:
            print(os.path.basename(self.base_dir) + "/")
            formatted_lines = self._format_tree(tree_data, prefix="", show_lines=show_lines)
            print("\n".join(formatted_lines))
        else:
            try: rel_path = os.path.relpath(self.base_dir, os.path.dirname(self.base_dir))
            except ValueError: rel_path = self.base_dir
            print(f"[无法访问基础目录 '{rel_path}']", file=sys.stderr)
        print("--- 树展示完毕 ---")


    def _build_visible_tree_recursive(self, current_dir_abs):
        """Recursive helper to build the tree data structure of visible items."""
        tree = {}
        try: entries = list(os.scandir(current_dir_abs))
        except OSError as e:
            try: rel_path = os.path.relpath(current_dir_abs, self.base_dir)
            except ValueError: rel_path = current_dir_abs
            print(f"错误: 无法访问目录 '{rel_path}' 以构建树: {e}", file=sys.stderr)
            return None # Indicate failure

        visible_entries = sorted(
            [entry for entry in entries if self.is_visible(entry.path)],
            key=lambda e: (not e.is_dir(), e.name.lower())
        )

        current_dir_proto = self.get_protocol(current_dir_abs)
        show_content_in_dir_preview = current_dir_proto.get("show_content", False)

        for entry in visible_entries:
            item_name = entry.name
            item_path_abs = entry.path

            if entry.is_dir():
                subtree = self._build_visible_tree_recursive(item_path_abs)
                if subtree is not None: tree[item_name] = subtree
            else: # File
                file_content_display = None
                ext = os.path.splitext(item_name)[1].lower()

                if ext in self.BINARY_EXTENSIONS:
                    if show_content_in_dir_preview: file_content_display = "[二进制文件，不显示内容预览]"
                elif ext in self.TEXT_EXTENSIONS:
                     if show_content_in_dir_preview:
                         try:
                              with open(item_path_abs, 'r', encoding='utf-8', errors='replace') as f:
                                 content = f.read()
                                 file_content_display = content
                         except Exception as e: file_content_display = f"[读取文件失败: {e}]"
                # else: Unknown type, content_display remains None

                tree[item_name] = file_content_display
        return tree


    def _format_tree(self, tree_dict, prefix="", show_lines=None):
        """Recursive helper to format the tree data into a list of strings."""
        lines = []
        # Sort items: directories first, then alphabetically
        sorted_items = sorted(tree_dict.items(), key=lambda item: (not isinstance(item[1], dict), item[0].lower()))

        num_items = len(sorted_items)
        for i, (name, value) in enumerate(sorted_items):
            is_last = (i == num_items - 1)
            connector = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")

            item_line = f"{prefix}{connector}{name}"
            if isinstance(value, dict): # Directory
                item_line += "/"
                lines.append(item_line)
                lines.extend(self._format_tree(value, next_prefix, show_lines))
            else: # File
                lines.append(item_line)
                if value is not None and isinstance(value, str): # Content/identifier string
                    content_lines = value.strip().splitlines()
                    display_content_lines = content_lines
                    if show_lines is not None and len(content_lines) > show_lines:
                        display_content_lines = content_lines[:show_lines]
                        display_content_lines.append(f"{next_prefix}... ({len(content_lines) - show_lines} more lines)")

                    content_prefixed_lines = [f"{next_prefix}{line}" for line in display_content_lines]
                    lines.extend(content_prefixed_lines)
        return lines


# --- Test Environment Setup and Execution ---
def setup_test_environment(base):
    """Creates a temporary directory structure and sample protocol files for testing."""
    base = os.path.abspath(base)
    print(f"\n--- 正在设置测试环境于: {base} ---")
    if os.path.exists(base):
        print(f"警告: 测试目录已存在，将先删除: {base}")
        try: shutil.rmtree(base)
        except OSError as e: print(f"错误: 无法删除现有测试目录 {base}: {e}", file=sys.stderr); raise

    try:
        # Create directories
        os.makedirs(os.path.join(base, "src"), exist_ok=True)
        os.makedirs(os.path.join(base, "docs"), exist_ok=True)
        os.makedirs(os.path.join(base, "tests"), exist_ok=True)
        os.makedirs(os.path.join(base, "data", "raw"), exist_ok=True)
        os.makedirs(os.path.join(base, "hidden_dir"), exist_ok=True)
        os.makedirs(os.path.join(base, "empty_dir"), exist_ok=True)

        # Create files
        with open(os.path.join(base, "README.md"), "w", encoding='utf-8') as f: f.write("# 项目说明\n")
        with open(os.path.join(base, "main.py"), "w", encoding='utf-8') as f: f.write("print('Hello main')\n")
        with open(os.path.join(base, ".gitignore"), "w", encoding='utf-8') as f: f.write("*.pyc\n")
        with open(os.path.join(base, "binary_file.dat"), "wb") as f: f.write(b'\x01\x02')
        with open(os.path.join(base, "src", "module.py"), "w", encoding='utf-8') as f: f.write("# src/module.py\n")
        with open(os.path.join(base, "src", "config.json"), "w", encoding='utf-8') as f: f.write('{"key": "value"}\n')
        with open(os.path.join(base, "docs", "index.html"), "w", encoding='utf-8') as f: f.write("<h1>Docs</h1>\n")
        with open(os.path.join(base, "data", "raw", "data1.csv"), "w", encoding='utf-8') as f: f.write("col1,col2\n1,2\n")
        with open(os.path.join(base, "tests", "test_main.py"), "w", encoding='utf-8') as f: f.write("assert True\n")
        with open(os.path.join(base, "hidden_dir", "secret.txt"), "w", encoding='utf-8') as f: f.write("Secret\n")

        # --- Create Protocol Files ---
        # Root: Allow creation
        base_proto = {
            "visible_files": ["README.md", "main.py", "src", "docs", "data", "tests", "empty_dir"],
            "operable_files": ["README.md", "main.py", "<create>"], # Allow creation in root
            "show_content": True
        }
        with open(os.path.join(base, "dirproto.json"), 'w', encoding='utf-8') as f: json.dump(base_proto, f, indent=4)
        print(f"创建协议: {os.path.join(base, 'dirproto.json')}")

        # Src: Inherit, allow creation, replace lists
        src_proto = {
            "inherit_parent": True, # Will inherit show_content=True from root
            "visible_files": ["module.py", "config.json"],
            "operable_files": ["module.py", "config.json", "<create>"], # Allow creation in src
            # show_content implicitly inherited and True
        }
        with open(os.path.join(base, "src", "dirproto.json"), 'w', encoding='utf-8') as f: json.dump(src_proto, f, indent=4)
        print(f"创建协议: {os.path.join(base, 'src', 'dirproto.json')}")

        # Data: No inherit, no creation
        data_proto = {
            "inherit_parent": False,
            "visible_files": ["raw"],
            "operable_files": [], # No creation allowed in data
            "show_content": False
        }
        with open(os.path.join(base, "data", "dirproto.json"), 'w', encoding='utf-8') as f: json.dump(data_proto, f, indent=4)
        print(f"创建协议: {os.path.join(base, 'data', 'dirproto.json')}")

        # Data/Raw: No inherit, allow creation, show content
        data_raw_proto = {
             "inherit_parent": False,
             "visible_files": ["data1.csv"],
             "operable_files": ["data1.csv", "<create>"], # Allow creation in data/raw
             "show_content": True
        }
        with open(os.path.join(base, "data", "raw", "dirproto.json"), 'w', encoding='utf-8') as f: json.dump(data_raw_proto, f, indent=4)
        print(f"创建协议: {os.path.join(base, 'data', 'raw', 'dirproto.json')}")

        # Docs: No creation, show content
        docs_proto = {
            "visible_files": ["index.html"],
            "operable_files": [], # No creation allowed
            "show_content": True
        }
        with open(os.path.join(base, "docs", "dirproto.json"), 'w', encoding='utf-8') as f: json.dump(docs_proto, f, indent=4)
        print(f"创建协议: {os.path.join(base, 'docs', 'dirproto.json')}")

        # Tests: Allow creation, show content
        tests_proto = {
            "visible_files": ["test_main.py"],
            "operable_files": ["test_main.py", "<create>"], # Allow creation
            "show_content": True
        }
        with open(os.path.join(base, "tests", "dirproto.json"), 'w', encoding='utf-8') as f: json.dump(tests_proto, f, indent=4)
        print(f"创建协议: {os.path.join(base, 'tests', 'dirproto.json')}")

        print("--- 测试环境设置完毕 ---")

    except Exception as e:
        print(f"设置测试环境时出错: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    TEST_DIR_NAME = "project_proto_test_2" # Changed name to avoid conflicts if run twice
    script_dir = os.path.dirname(os.path.abspath(__file__))
    TEST_DIR = os.path.join(script_dir, TEST_DIR_NAME)

    try:
        setup_test_environment(TEST_DIR)
        manager = DirProtoManager(TEST_DIR)
        manager.initialize_protocols() # Ensure empty ones exist
        manager.load_protocols()

        print("\n--- 初始状态 ---")
        manager.display_tree(show_lines=3)

        print("\n--- 执行创建和修改命令 ---")
        # --- Creation Tests ---
        # Success: Create file in root (allowed by root protocol)
        manager.execute_command("touch new_root_file.txt")
        # Success: Create dir in root (allowed by root protocol)
        manager.execute_command("mkdir new_root_dir")
        # Success: Create file in src (allowed by src protocol)
        manager.execute_command("touch src/new_src_file.log")
        # Success: Create nested dir/file in tests (allowed by tests protocol)
        manager.execute_command("mkdir tests/subdir")
        manager.execute_command("touch tests/subdir/nested_test.py")
        # Fail: Create file in data (not allowed by data protocol)
        manager.execute_command("touch data/forbidden_file.txt")
        # Fail: Create dir in docs (not allowed by docs protocol)
        manager.execute_command("mkdir docs/forbidden_subdir")
        # Fail: Create file that already exists
        manager.execute_command("touch main.py")
        # Fail: Create dir that already exists
        manager.execute_command("mkdir src")
        # Success: Create file in data/raw (allowed by data/raw protocol)
        manager.execute_command("touch data/raw/another_data_file.csv")

        # --- Other Operations (check interaction) ---
        # Modify newly created file (needs <create> in parent AND file name in operable, OR just <create> if using '=' ?)
        # Let's test '=' with a new file - relies on <create> in parent
        manager.execute_command("new_root_file.txt = \"Initial content for new file.\"")
        # Delete newly created directory
        manager.execute_command("new_root_dir ×")
        # Move a file into a newly created directory (source needs move permission, dest needs create permission if target name is new)
        # Move main.py (operable in root) to tests/subdir (subdir exists, created via mkdir)
        # Note: shutil.move might overwrite if tests/subdir/main.py existed. Our command doesn't check target existence explicitly here.
        manager.execute_command("main.py -> tests/subdir/main_moved_here.py")


        # Important: Newly created files/dirs are NOT automatically visible!
        # They need to be added to the parent's "visible_files" list by another command or manually.

        print("\n--- 重新加载协议 (包含新目录的空协议) ---")
        manager.load_protocols() # Reload to potentially include protocols for new_root_dir, tests/subdir etc.

        print("\n--- 操作后的状态 (注意: 新项目默认不可见!) ---")
        manager.display_tree(show_lines=3)

        # --- Visibility Example ---
        # Make the new file in src visible
        print("\n--- 使 src/new_src_file.log 可见 ---")
        # Read existing src protocol
        src_proto_path = os.path.join(manager.base_dir, "src", "dirproto.json")
        updated_src_proto = {}
        try:
            with open(src_proto_path, 'r', encoding='utf-8') as f:
                 updated_src_proto = json.load(f)
            # Add the new file to visible_files
            if "visible_files" not in updated_src_proto: updated_src_proto["visible_files"] = []
            if "new_src_file.log" not in updated_src_proto["visible_files"]:
                updated_src_proto["visible_files"].append("new_src_file.log")
                # Write it back using an execute_command (need quotes escaped within the command string)
                # Using json.dumps ensures correct JSON formatting including quotes.
                new_proto_content_str = json.dumps(updated_src_proto, ensure_ascii=False)
                # Need to escape quotes for the command parser
                command_content = new_proto_content_str.replace('"', '\\"')
                manager.execute_command(f'src/dirproto.json = "{command_content}"') # Use = to overwrite

                print("\n--- 重新加载协议以反映可见性更改 ---")
                manager.load_protocols()
                print("\n--- 更新可见性后的树 ---")
                manager.display_tree(show_lines=3)
            else:
                print("文件 'src/new_src_file.log' 已在协议中可见。")

        except Exception as e:
            print(f"更新 src 协议以使文件可见时出错: {e}")


        # --- Test read_file_content on newly created file ---
        print("\n--- 测试读取新创建的文件内容 ---")
        content_new = manager.read_file_content("new_root_file.txt")
        # This should fail because new_root_file.txt is not in root's visible_files
        if content_new is not None:
            print("成功读取 new_root_file.txt:")
            print(content_new)
        else:
            print("无法读取 new_root_file.txt (预期行为，因为它在父协议中不可见)")


    except Exception as main_e:
        print(f"\n主程序执行过程中发生错误: {main_e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

    finally:
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