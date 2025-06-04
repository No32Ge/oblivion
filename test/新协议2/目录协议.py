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
        "operable_files": ["file1.txt", "script.py"], # 在此目录中可操作 (编辑/删除/移动源) 的文件列表
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
        # Use commonpath for a robust check
        if os.path.commonpath([abs_dir_path, self.base_dir]) != self.base_dir:
            # print(f"Skipping initialization outside base_dir: {abs_dir_path}", file=sys.stderr) # Usually not needed to print
            return

        proto_path = os.path.join(abs_dir_path, "dirproto.json")

        # Check if file exists, create if not
        if not os.path.exists(proto_path):
            try:
                # Create empty file and write {}
                with open(proto_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f) # Write an empty JSON object
                # print(f"Initialized empty protocol file: {proto_path}") # Too verbose, print in test script
            except OSError as e:
                print(f"错误: 无法创建协议文件 {proto_path}: {e}", file=sys.stderr)
            except Exception as e: # Catch other potential errors
                 print(f"错误: 创建协议文件 {proto_path} 时发生意外错误: {e}", file=sys.stderr)
        # else: # File already exists, do nothing
        #    pass

        # Recursively enter subdirectories
        try:
            # Using scandir might be more performant
            for entry in os.scandir(abs_dir_path):
                if entry.is_dir():
                    # Recursively call itself for subdirectories
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
            # print(f"DEBUG_LOAD_RECUR: Skipping '{os.path.relpath(abs_dir_path, self.base_dir) if os.path.exists(self.base_dir) else abs_dir_path}' (already loaded or outside base)") # Verbose skip debug
            return

        proto_path = os.path.join(abs_dir_path, "dirproto.json")
        proto = {}

        if os.path.exists(proto_path) and os.path.isfile(proto_path):
            try:
                with open(proto_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        proto = json.loads(content)
                        print(f"DEBUG_LOAD_RECUR: Loaded protocol from '{os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path}'")
                    else:
                       print(f"DEBUG_LOAD_RECUR: Protocol file empty: '{os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path}'. Using empty protocol.")

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
             print(f"DEBUG_LOAD_RECUR: Protocol file not found: '{os.path.relpath(proto_path, self.base_dir) if os.path.exists(self.base_dir) else proto_path}'. Using empty protocol.") # Debug info
             proto = {}

        # --- Handle Inheritance ---
        # Only inherit if inherit_parent is True in the current protocol AND it's not the base directory
        if proto.get("inherit_parent", False) and abs_dir_path != self.base_dir:
            parent_dir = os.path.dirname(abs_dir_path)
            # Ensure parent protocol is loaded (recursive call guarantees this, or explicit load)
            # Ensure parent is within base_dir
            if os.path.commonpath([parent_dir, self.base_dir]) == self.base_dir:
                 if parent_dir not in self.protocols:
                     print(f"DEBUG_LOAD_RECUR: Recursively loading parent protocol for '{os.path.relpath(abs_dir_path, self.base_dir) if os.path.exists(self.base_dir) else abs_dir_path}': '{os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir}'") # Debug
                     self.load_protocol_recursive(parent_dir) # Ensure parent is loaded

                 parent_proto = self.protocols.get(parent_dir, {})
                 if parent_proto:
                      print(f"DEBUG_LOAD_RECUR: Merging protocol for '{os.path.relpath(abs_dir_path, self.base_dir) if os.path.exists(self.base_dir) else abs_dir_path}' from parent '{os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir}'") # Debug info
                      proto = self.merge_protocol(parent_proto, proto)
            else:
                # Parent directory is outside base_dir, cannot inherit
                try:
                     rel_abs_dir = os.path.relpath(abs_dir_path, self.base_dir)
                     rel_parent_dir = os.path.relpath(parent_dir, os.path.dirname(parent_dir)) # Relative to its own parent if outside base
                except ValueError:
                     rel_abs_dir = abs_dir_path
                     rel_parent_dir = parent_dir
                print(f"警告: 路径 '{rel_abs_dir}' 尝试继承其父目录 '{rel_parent_dir}'，但父目录超出基础目录 '{self.base_dir}' 范围，忽略继承。", file=sys.stderr)


        # Store the final effective protocol for the current directory
        self.protocols[abs_dir_path] = proto
        # Using os.path.relpath for printing key for readability if base_dir exists
        print(f"DEBUG_LOAD_STORE: Stored protocol for '{os.path.relpath(abs_dir_path, self.base_dir) if os.path.exists(self.base_dir) else abs_dir_path}'. Total keys in protocols: {len(self.protocols)}")


        # --- Recurse into subdirectories ---
        try:
            # Using scandir might be more performant
            for entry in os.scandir(abs_dir_path):
                if entry.is_dir():
                    # Recursively load subdirectory protocols
                    self.load_protocol_recursive(entry.path)
        except OSError as e:
            try:
                 rel_path = os.path.relpath(abs_dir_path, self.base_dir)
            except ValueError:
                 rel_path = abs_dir_path
            print(f"错误: 无法列出目录以加载子协议 {rel_path}: {e}", file=sys.stderr)
        # --- End Recursion ---


    def load_protocols(self):
        """
        Loads all protocol files under the base directory.
        """
        print(f"\n--- 开始从 '{self.base_dir}' 加载协议 ---")
        self.protocols = {} # Clear old protocols before reloading
        if os.path.isdir(self.base_dir):
            self.load_protocol_recursive(self.base_dir)
        else:
            print(f"错误: 无法加载协议，因为基础目录 '{self.base_dir}' 不存在或不是目录。", file=sys.stderr)
        print("--- 协议加载完成 ---")


    def merge_protocol(self, parent, child):
        """
        Merges parent protocol and child protocol. Child keys/values override parent keys/values.
        Note: For lists like visible_files, the child list completely replaces the parent list.
              The 'inherit_parent' key itself is simply overwritten if present in child.
        This simplified version relies on the caller checking inherit_parent before calling.
        """
        merged = parent.copy()
        merged.update(child)
        return merged


    # --- Protocol Lookup and Checks ---
    def get_protocol(self, item_path):
        """
        Gets the effective protocol for the directory containing the specified file or directory path.
        If the directory itself doesn't have a protocol, it looks up its parent's protocol,
        traversing up until a protocol is found or the base directory is reached.
        """
        abs_item_path = os.path.abspath(item_path)
        # Get the directory path for the item
        if os.path.isdir(abs_item_path):
            dir_path = abs_item_path
        else:
            dir_path = os.path.dirname(abs_item_path)

        # Traverse upwards to find a protocol until one is found or the base_dir is reached
        current_dir = dir_path
        # Use commonpath to ensure traversal stays within or reaches the base_dir
        # The loop condition checks if current_dir is equal to base_dir OR if base_dir is an ancestor of current_dir
        while os.path.commonpath([current_dir, self.base_dir]) == self.base_dir:

            # --- DEBUG GET_PROTOCOL ---
            try:
                rel_current_dir = os.path.relpath(current_dir, self.base_dir)
            except ValueError: # Handle case where current_dir is above base_dir but commonpath check failed (shouldn't happen with this loop)
                 rel_current_dir = current_dir # Use absolute path if relative fails

            # Debug print inside the loop showing the current dir being checked and the keys present
            print(f"DEBUG_GET_PROTOCOL:   Checking '{current_dir}' (relative: '{rel_current_dir}') in self.protocols. Keys present count: {len(self.protocols)}. Keys: {list(self.protocols.keys())}")
            # --- END DEBUG GET_PROTOCOL ---

            proto = self.protocols.get(current_dir)
            if proto is not None: # Found a protocol
                # --- DEBUG GET_PROTOCOL ---
                # (Detailed info already printed above)
                print(f"DEBUG_GET_PROTOCOL:   Found protocol for '{current_dir}'")
                # --- END DEBUG GET_PROTOCOL ---
                return proto

            # If we've reached the base_dir and no protocol was found (shouldn't happen if loaded)
            if current_dir == self.base_dir:
                # print(f"DEBUG_GET_PROTOCOL: Reached base_dir '{self.base_dir}', stopping traversal.") # Debug
                break # Avoid infinite loop

            # Move to the parent directory
            parent = os.path.dirname(current_dir)
            # Prevent infinite loop (e.g., at the file system root)
            if parent == current_dir:
                 # print(f"DEBUG_GET_PROTOCOL: Reached file system root from '{current_dir}', stopping traversal.") # Debug
                 break
            current_dir = parent

        # print(f"DEBUG_GET_PROTOCOL: Traversal ended for '{os.path.relpath(abs_item_path, self.base_dir) if os.path.exists(abs_item_path) else abs_item_path}'. No protocol found up to base_dir.") # Debug


        # If no protocol is found up the hierarchy within base_dir, return an empty one
        return {}

    def is_visible(self, item_path):
        """
        Checks if a file or directory is marked as visible in the protocol of its *parent directory*.
        """
        abs_item_path = os.path.abspath(item_path)
        parent_dir_path = os.path.dirname(abs_item_path)
        item_name = os.path.basename(abs_item_path)

        # If the item is the base_dir itself, it's always the visible root
        if abs_item_path == self.base_dir:
            return True

        # If the parent directory is outside the base_dir, it's not visible
        # Use os.path.commonpath for a robust check, including drive letters on Windows
        if os.path.commonpath([parent_dir_path, self.base_dir]) != self.base_dir:
             # print(f"DEBUG_VISIBLE: Item='{item_name}', Parent='{os.path.relpath(parent_dir_path, self.base_dir) if os.path.exists(parent_dir_path) else parent_dir_path}'. Parent outside base_dir. Invisible.") # Debug
             print(f"DEBUG_VISIBLE: Item='{item_name}', Parent='{parent_dir_path}'. Parent outside base_dir '{self.base_dir}'. Invisible.")
             return False

        # Get the protocol applied to the parent directory
        parent_proto = self.get_protocol(parent_dir_path) # Pass the parent directory path directly

        visible_list = parent_proto.get("visible_files", [])

        # --- DEBUG VISIBLE ---
        try:
            rel_parent_dir_path = os.path.relpath(parent_dir_path, self.base_dir)
        except ValueError:
            rel_parent_dir_path = parent_dir_path

        is_item_visible = item_name in visible_list
        print(f"DEBUG_VISIBLE: Item='{item_name}', Parent='{rel_parent_dir_path}', VisibleList={visible_list}, IsVisible={is_item_visible}") # Debug
        # --- END DEBUG VISIBLE ---

        return is_item_visible


    def is_operable(self, item_path):
        """
        Checks if a file is marked as operable in the protocol of its *containing directory*.
        Note: Directories are not considered operable by this method.
        """
        abs_item_path = os.path.abspath(item_path)
        if not os.path.isfile(abs_item_path):
             # print(f"DEBUG_OPERABLE: Item='{os.path.relpath(abs_item_path, self.base_dir) if os.path.exists(abs_item_path) else abs_item_path}' is not a file. Not operable.") # Debug
             return False # Only files are operable

        # Get the protocol for the directory containing the file
        proto = self.get_protocol(abs_item_path) # Pass the file path to get its directory's protocol
        item_name = os.path.basename(abs_item_path)

        operable_list = proto.get("operable_files", [])

        # --- DEBUG OPERABLE ---
        try:
            rel_dir_path = os.path.relpath(os.path.dirname(abs_item_path), self.base_dir)
        except ValueError:
             rel_dir_path = os.path.dirname(abs_item_path)

        is_item_operable = item_name in operable_list
        print(f"DEBUG_OPERABLE: Item='{item_name}', Dir='{rel_dir_path}', OperableList={operable_list}, IsOperable={is_item_operable}") # Debug
        # --- END DEBUG OPERABLE ---

        return is_item_operable


    def should_show_content_preview(self, file_path):
        """
        Checks if a file's content preview should be shown in the tree display according to its containing directory's protocol.
        Only effective for text files.
        """
        abs_file_path = os.path.abspath(file_path)
        if not os.path.isfile(abs_file_path):
            return False

        # Check if the file extension is a text file extension
        ext = os.path.splitext(abs_file_path)[1].lower()
        if ext not in self.TEXT_EXTENSIONS:
            # print(f"文件 {os.path.basename(abs_file_path)} 不是文本文件，不显示内容") # 调试
            return False

        # Get the protocol for the directory containing the file
        proto = self.get_protocol(abs_file_path) # Pass the file path to get its directory's protocol
        # Check if the protocol has the "show_content" key and its value is True
        return proto.get("show_content", False) # Default to False

    # --- Auxiliary Function ---
    def _get_abs_path(self, relative_path):
        """
        Helper function: Converts a path relative to base_dir to an absolute path.
        Performs security check to ensure the path stays within base_dir.
        """
        # Clean up relative path (e.g., remove leading '/', handle '..')
        # os.path.join handles joining, os.path.abspath resolves '..' relative to cwd,
        # os.path.normpath normalizes the path string.
        # We need to ensure the *final* absolute path is within base_dir.

        # Start from base_dir and join the relative path
        full_path = os.path.join(self.base_dir, relative_path)
        # Resolve to an absolute and normalized path
        abs_path = os.path.normpath(os.path.abspath(full_path))

        # Security check: Ensure the resulting path is within or is the base_dir
        # Use os.path.commonpath for robust check, including drive letters on Windows
        if os.path.commonpath([abs_path, self.base_dir]) == self.base_dir:
             return abs_path
        else:
            # If the calculated path is outside base_dir, it might be malicious or an error
            try:
                 rel_path = os.path.relpath(abs_path, self.base_dir) # Relative to base_dir for printing
            except ValueError:
                 rel_path = abs_path # Use absolute if relpath fails (e.g. different drive)

            print(f"警告: 尝试访问基础目录之外的路径 '{relative_path}' -> '{abs_path}' (计算结果超出: '{self.base_dir}')", file=sys.stderr)
            return None # Or raise ValueError("Access outside base directory is not allowed")


    # --- File Content Reading (Designed for AI Copilot or other full-content needs) ---
    def read_file_content(self, file_path):
        """
        Reads the full content of the specified file.
        The file must be visible according to the protocol.
        Returns string content for text files, a specific identifier for binary files.
        Returns None if the path is invalid, the file doesn't exist, is not a file, or is not visible.
        """
        abs_file_path = self._get_abs_path(file_path)

        if abs_file_path is None:
            print(f"错误: 无效的或超出范围的路径: '{file_path}'", file=sys.stderr)
            return None # Or raise ValueError

        if not os.path.exists(abs_file_path):
             print(f"错误: 文件不存在: '{file_path}'", file=sys.stderr)
             return None

        if not os.path.isfile(abs_file_path):
             print(f"错误: 路径不是一个文件: '{file_path}'", file=sys.stderr)
             return None

        # Check if the file is visible
        if not self.is_visible(abs_file_path):
             # is_visible already prints debug info if needed.
             # print(f"ERROR: File '{file_path}' is not visible according to protocol, cannot read content.", file=sys.stderr) # Debug is_visible will print details
             print(f"错误: 文件 '{file_path}' 根据协议不可见，无法读取内容。", file=sys.stderr) # Simplified user message
             return None # Or raise PermissionError

        # Check file type
        ext = os.path.splitext(abs_file_path)[1].lower()

        if ext in self.BINARY_EXTENSIONS:
            # For binary files, return an identifier instead of reading actual content
            print(f"警告: 尝试读取二进制文件内容: '{file_path}'", file=sys.stderr)
            return "[这是一个二进制文件，不显示其内容]"

        elif ext in self.TEXT_EXTENSIONS:
            # For text files, read and return full content
            try:
                with open(abs_file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                # print(f"已读取文件 '{file_path}' 的全部内容") # Too verbose, only print on success in test script
                return content
            except Exception as e:
                print(f"错误: 读取文件 '{file_path}' 失败: {e}", file=sys.stderr)
                return f"[读取文件失败: {e}]"
        else:
             # For unknown file types, return None or a generic identifier
             print(f"警告: 尝试读取未知文件类型内容: '{file_path}'", file=sys.stderr)
             return "[未知类型文件，不显示内容]"


    # --- Command Execution ---
    def execute_command(self, command):
        """
        Parses and executes file operation commands based on directory protocols.

        Supported command formats:
        - "source_file/dir -> dest_file/dir" (Move/Rename)
        - "file ×"                      (Delete file/dir)
        - "file += \"content\""            (Append content to file)
        - "file = \"content\""             (Overwrite content to file)
        """
        print(f"\n执行指令: {command}")
        command = command.strip()

        try:
            # --- Move Operation ---
            if "->" in command:
                parts = command.split("->", 1)
                if len(parts) != 2:
                    print(f"格式错误 (->): '{command}'", file=sys.stderr); return
                src_rel, dest_rel = map(str.strip, parts)
                src_path = self._get_abs_path(src_rel)
                dest_path = self._get_abs_path(dest_rel)

                if src_path is None or dest_path is None: return # Invalid path or outside base_dir
                if not os.path.exists(src_path): print(f"错误: 源 '{src_rel}' 不存在"); return

                # Move operation checks permission of the source item (if it's a file).
                # Directories are not controlled by operable_files, but must be within base_dir.
                if os.path.isfile(src_path):
                     if not self.is_operable(src_path):
                         print(f"无权限操作源文件: '{src_rel}'")
                         return
                # If the source is a directory, it can be moved as long as it's within base_dir (guaranteed by _get_abs_path)

                try:
                    # Ensure the target directory exists
                    dest_parent_dir = os.path.dirname(dest_path)
                    # Check if dest_parent_dir is within base_dir (already done by _get_abs_path for dest_path, but belt and suspenders)
                    if os.path.commonpath([dest_parent_dir, self.base_dir]) != self.base_dir:
                         print(f"错误: 目标目录 '{dest_rel}' 超出基础目录范围。", file=sys.stderr)
                         return

                    if not os.path.exists(dest_parent_dir):
                        os.makedirs(dest_parent_dir, exist_ok=True)
                        # No further visibility check on the newly created directory or its parent needed here

                    shutil.move(src_path, dest_path)
                    print(f"已移动: '{src_rel}' -> '{dest_rel}'")
                    # Note: Move operation changes the protocol environment of the item, but protocols are not automatically reloaded here
                except OSError as e:
                    print(f"移动错误: '{src_rel}' -> '{dest_rel}': {e}", file=sys.stderr)
                except Exception as e:
                     print(f"移动 '{src_rel}' -> '{dest_rel}' 时发生意外错误: {e}", file=sys.stderr)


            # --- Delete Operation ---
            elif command.endswith("×"):
                item_rel = command[:-1].strip() # Can be file or directory
                item_path = self._get_abs_path(item_rel)

                if item_path is None: return # Invalid path
                if not os.path.exists(item_path): print(f"错误: 项目 '{item_rel}' 不存在"); return

                # Delete operation checks permission if it's a file. Directories can be deleted if within base_dir.
                if os.path.isfile(item_path):
                     if not self.is_operable(item_path):
                         print(f"无权限删除文件: '{item_rel}'")
                         return
                # If it's a directory, it can be deleted as long as it's within base_dir (guaranteed by _get_abs_path)

                try:
                    if os.path.isfile(item_path):
                         os.remove(item_path)
                         print(f"已删除文件: '{item_rel}'")
                    elif os.path.isdir(item_path):
                         # Recursively delete directory
                         shutil.rmtree(item_path)
                         print(f"已删除目录: '{item_rel}'")
                    else:
                         print(f"警告: 无法删除特殊文件类型 '{item_rel}'", file=sys.stderr)

                except OSError as e: print(f"删除错误: '{item_rel}': {e}", file=sys.stderr)
                except Exception as e: print(f"删除 '{item_rel}' 时发生意外错误: {e}", file=sys.stderr)


            # --- Append or Overwrite Operation ---
            elif "+=" in command or "=" in command:
                operator = "+=" if "+=" in command else "="
                parts = command.split(operator, 1)
                if len(parts) == 2:
                    file_rel, content_part = map(str.strip, parts)
                    # Simple removal of quotes from content, handle basic escapes
                    content = content_part
                    if content.startswith('"') and content.endswith('"'):
                         content = content[1:-1]
                         content = content.replace('\\n', '\n').replace('\\"', '"')
                    elif content.startswith("'") and content.endswith("'"):
                         content = content[1:-1]
                         content = content.replace('\\n', '\n').replace("\\'", "'")
                    # If no quotes, use content_part directly

                    file_path = self._get_abs_path(file_rel)

                    if file_path is None: return # Invalid path

                    # Cannot write content to a directory
                    if os.path.isdir(file_path):
                         print(f"错误: 无法向目录 '{file_rel}' 写入内容。", file=sys.stderr)
                         return

                    # Check if the target file path (even if it doesn't exist) is operable
                    # Note: is_operable checks the protocol of the target file's directory and whether the file name is in operable_files
                    if self.is_operable(file_path):
                        try:
                            # Ensure the target directory exists
                            parent_dir = os.path.dirname(file_path)
                             # Check if parent_dir is within base_dir (already done by _get_abs_path for file_path, but belt and suspenders)
                            if os.path.commonpath([parent_dir, self.base_dir]) != self.base_dir:
                                 print(f"错误: 目标文件父目录 '{os.path.relpath(parent_dir, self.base_dir) if os.path.exists(self.base_dir) else parent_dir}' 超出基础目录范围。", file=sys.stderr)
                                 return

                            if not os.path.exists(parent_dir):
                                os.makedirs(parent_dir, exist_ok=True)
                                # No further visibility check on the newly created directory or its parent needed here

                            mode = "a" if operator == "+=" else "w"
                            # Check if it's a text file. Binary files cannot be directly written with text content.
                            ext = os.path.splitext(file_path)[1].lower()
                            # Only text files or non-existent paths (which will be created as text files) are allowed for content writing
                            if os.path.exists(file_path) and ext not in self.TEXT_EXTENSIONS:
                                print(f"错误: 无法使用文本内容操作符 ({operator}) 修改非文本文件 '{file_rel}'", file=sys.stderr)
                                return

                            with open(file_path, mode, encoding='utf-8') as f:
                                f.write(content) # Write the processed string
                                # Optional: If appending and content doesn't end with newline, add one for next append
                                # if operator == "+=" and not content.endswith('\n'):
                                #      f.write('\n')

                            print(f"已使用 '{operator}' 更新文件 '{file_rel}'")
                        except OSError as e: print(f"文件写入错误 ({operator}): '{file_rel}': {e}", file=sys.stderr)
                        except Exception as e: print(f"更新文件 '{file_rel}' 时发生意外错误: {e}", file=sys.stderr)
                    else:
                        # Provide more specific permission info
                        if os.path.exists(file_path): print(f"无权限编辑文件: '{file_rel}'")
                        else: print(f"无权限创建或编辑文件: '{file_rel}'")
                else: print(f"格式错误 ({operator}): '{command}'", file=sys.stderr)


            # --- Unknown Command ---
            else: print(f"无法识别的指令: '{command}'", file=sys.stderr)

        except Exception as e:
             print(f"处理指令时发生意外错误 '{command}': {e}", file=sys.stderr)
             # Optionally print traceback for more detailed debugging
             # import traceback
             # traceback.print_exc()


    # --- Directory Tree Display ---
    def display_tree(self, show_lines=None):
        """
        Displays visible files and directories in a tree structure according to the protocol.
        Optional parameter show_lines: If specified, limits the number of lines shown for each visible text file's content.
        """
        # Ensure protocols are loaded
        if not self.protocols:
            print("协议尚未加载，现在开始加载...")
            self.load_protocols() # Call the public loading method
            if not self.protocols:
                print("错误: 协议加载失败，无法展示目录树。", file=sys.stderr)
                return

        print(f"\n--- 可见文件/目录树 ({os.path.basename(self.base_dir)}) ---")
        # The base directory itself is always the visible root

        # Build the tree data structure
        tree_data = self._build_visible_tree_recursive(self.base_dir)

        # Format and print the tree structure
        if tree_data is not None: # If the root directory was successfully built (not None)
            # Print the base directory name as the root
            print(os.path.basename(self.base_dir) + "/")
            # Format and print the children items
            formatted_lines = self._format_tree(tree_data, prefix="", show_lines=show_lines)
            print("\n".join(formatted_lines))
        else:
            try:
                 rel_path = os.path.relpath(self.base_dir, os.path.dirname(self.base_dir))
            except ValueError:
                 rel_path = self.base_dir
            print(f"[无法访问基础目录 '{rel_path}']", file=sys.stderr)


        print("--- 树展示完毕 ---")


    def _build_visible_tree_recursive(self, current_dir_abs):
        """
        Recursive helper function to build the tree data structure of visible items.
        Returns a dictionary where keys are item names, and values are either a sub-dictionary (for directories)
        or file content/identifier (for files).
        Returns None if the directory is inaccessible.
        """
        tree = {}
        try:
            # Use scandir to get a list of directory entry objects
            entries = list(os.scandir(current_dir_abs))
        except OSError as e:
            # If the directory is inaccessible, log an error and return None
            try:
                 rel_path = os.path.relpath(current_dir_abs, self.base_dir)
            except ValueError:
                 rel_path = current_dir_abs
            print(f"错误: 无法访问目录 '{rel_path}' 以构建树: {e}", file=sys.stderr)
            return None # Return None to indicate failure or permission error

        # Filter for visible items (is_visible checks the entry's visibility in current_dir_abs's protocol)
        visible_entries = sorted(
            [entry for entry in entries if self.is_visible(entry.path)],
            key=lambda e: (not e.is_dir(), e.name.lower()) # Directories first, then sort by name
        )

        # Get the protocol for the current directory to determine if content preview should be shown
        current_dir_proto = self.get_protocol(current_dir_abs)
        show_content_in_dir_preview = current_dir_proto.get("show_content", False)


        # Iterate through visible items
        for entry in visible_entries:
            item_name = entry.name
            item_path_abs = entry.path

            if entry.is_dir():
                # If it's a directory, recursively build the subtree
                subtree = self._build_visible_tree_recursive(item_path_abs)
                # If the subtree was built successfully (not None), add it to the tree
                if subtree is not None:
                    tree[item_name] = subtree
                # else: If the subdirectory is inaccessible, it won't be added to the current tree (or could add an error node)
                # Current implementation: If a subdirectory is inaccessible, it and its contents won't appear in the tree.
            else: # It's a file
                file_content_display = None # Default to not showing content or showing a specific identifier

                # Check file type
                ext = os.path.splitext(item_name)[1].lower()

                if ext in self.BINARY_EXTENSIONS:
                    # If it's a binary file, even if the protocol asks for preview, only show a marker
                    if show_content_in_dir_preview:
                        file_content_display = "[二进制文件，不显示内容预览]"
                elif ext in self.TEXT_EXTENSIONS:
                     # If it's a text file and the protocol asks for preview
                     if show_content_in_dir_preview:
                         try:
                             # Read the file content for display in the tree (format_tree will handle line limits)
                             # To avoid loading huge files into memory for just a preview, could limit the read size here.
                             # For AI copilot needing full content, they'd use read_file_content anyway.
                              with open(item_path_abs, 'r', encoding='utf-8', errors='replace') as f:
                                 content = f.read()
                                 file_content_display = content # Store the full content; format_tree handles display truncation

                         except Exception as e:
                             file_content_display = f"[读取文件失败: {e}]"
                     # else: show_content_in_dir_preview is False, file_content_display remains None
                # else: Neither text nor binary extensions, file_content_display remains None

                # Add the file to the tree structure
                # The value is either the content string, None (no content shown), or a specific identifier string
                tree[item_name] = file_content_display

        return tree # Return the built subtree structure for the current directory


    def _format_tree(self, tree_dict, prefix="", show_lines=None):
        """
        Recursive helper function to format the tree data structure into a list of strings with indentation.
        tree_dict: The dictionary structure built by _build_visible_tree_recursive.
        prefix: The indentation prefix for the current level.
        show_lines: Optional, limits the number of lines of file content to display.
        """
        lines = []
        # Sort items by name (case-insensitive), directories first
        from operator import itemgetter
        # tree_dict.items() gives (key, value) pairs
        # Sorting criteria: (is_directory_flag, lower_case_name)
        # is_directory_flag: not isinstance(item[1], dict) -> if value is a dict (directory), isinstance is True, not True is False, so directories sort before files.
        # lower_case_name: item[0].lower() -> sort alphabetically by name, ignoring case.
        sorted_items = sorted(tree_dict.items(), key=lambda item: (not isinstance(item[1], dict), item[0].lower()))


        num_items = len(sorted_items)
        for i, (name, value) in enumerate(sorted_items):
            is_last = (i == num_items - 1)
            # Choose connector and next level prefix based on whether it's the last item
            connector = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")

            # Add the line for the current item
            item_line = f"{prefix}{connector}{name}"
            if isinstance(value, dict): # Is a directory (value is a sub-dictionary)
                item_line += "/" # Add a slash to directory names
                lines.append(item_line)
                # Recursively format the subdirectory
                lines.extend(self._format_tree(value, next_prefix, show_lines))
            else: # Is a file (value is content string, None, or identifier string)
                lines.append(item_line)
                if value is not None: # If there's content or a specific identifier to display
                    if isinstance(value, str):
                         # If it's a string content or identifier
                         content_lines = value.strip().splitlines()
                         display_content_lines = content_lines

                         if show_lines is not None and len(content_lines) > show_lines:
                             display_content_lines = content_lines[:show_lines]
                             # Add ellipsis marker
                             display_content_lines.append(f"{next_prefix}... ({len(content_lines) - show_lines} more lines)") # Add indentation to ellipsis marker

                         # Format content lines with indentation
                         content_prefixed_lines = [f"{next_prefix}{line}" for line in display_content_lines]
                         lines.extend(content_prefixed_lines)
                    # else: value is not None but not a string? (Shouldn't happen with current build logic)
                    # If needed, could add a default conversion: [f"{next_prefix}{str(value)}"]
        return lines


# --- Test Environment Setup and Execution ---
def setup_test_environment(base):
    """Creates a temporary directory structure and sample protocol files for testing."""
    base = os.path.abspath(base) # Ensure base is an absolute path
    print(f"\n--- 正在设置测试环境于: {base} ---")
    if os.path.exists(base):
        print(f"警告: 测试目录已存在，将先删除: {base}")
        try:
            shutil.rmtree(base)
        except OSError as e:
            print(f"错误: 无法删除现有测试目录 {base}: {e}", file=sys.stderr)
            # If deletion fails, try to proceed (might lead to other issues) or exit directly
            # raise # If strict behavior is needed, re-raise the exception

    try:
        # Create directory structure
        os.makedirs(base, exist_ok=True) # Use exist_ok to prevent errors if deletion failed
        os.makedirs(os.path.join(base, "src"), exist_ok=True)
        os.makedirs(os.path.join(base, "docs"), exist_ok=True)
        os.makedirs(os.path.join(base, "tests"), exist_ok=True)
        os.makedirs(os.path.join(base, "data", "raw"), exist_ok=True) # Nested subdirectory
        os.makedirs(os.path.join(base, "hidden_dir"), exist_ok=True)
        os.makedirs(os.path.join(base, "empty_dir"), exist_ok=True) # For testing empty directory visibility

        # Create sample files
        with open(os.path.join(base, "README.md"), "w", encoding='utf-8') as f: f.write("# 项目说明\n这是一个示例项目，用于测试目录协议管理器。\n")
        with open(os.path.join(base, "main.py"), "w", encoding='utf-8') as f: f.write("print('Hello main')\n")
        with open(os.path.join(base, ".gitignore"), "w", encoding='utf-8') as f: f.write("*.pyc\n__pycache__/\n")
        with open(os.path.join(base, "binary_file.dat"), "wb") as f: f.write(b'\x01\x02\x03') # Binary file
        with open(os.path.join(base, "src", "module.py"), "w", encoding='utf-8') as f: f.write("# src/module.py\ndef func(): pass\n\n# This is a comment\n")
        with open(os.path.join(base, "src", "config.json"), "w", encoding='utf-8') as f: f.write('{\n    "key": "value",\n    "list": [1, 2, 3]\n}\n')
        with open(os.path.join(base, "docs", "index.html"), "w", encoding='utf-8') as f: f.write("<!DOCTYPE html>\n<html><body><h1>Docs</h1></body></html>\n")
        with open(os.path.join(base, "data", "raw", "data1.csv"), "w", encoding='utf-8') as f: f.write("col1,col2\n1,2\n3,4\n5,6\n7,8\n9,10\n11,12\n") # Multi-line content
        with open(os.path.join(base, "tests", "test_main.py"), "w", encoding='utf-8') as f: f.write("assert True # Test passes\n")
        with open(os.path.join(base, "hidden_dir", "secret.txt"), "w", encoding='utf-8') as f: f.write("Secret content that should not be seen.\n")


        # --- Create Protocol Files ---
        # Root directory protocol
        base_proto = {
            "visible_files": ["README.md", "main.py", "src", "docs", "data", "tests", "empty_dir"], # .gitignore, binary_file.dat, and hidden_dir are not visible
            "operable_files": ["README.md", "main.py"], # Only these two files are operable in the root
            "show_content": True # Show content preview for text files in the root
        }
        with open(os.path.join(base, "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(base_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'dirproto.json')}")

        # src directory protocol (Inherit and add, also show content preview)
        src_proto = {
            "inherit_parent": True,
            "visible_files": ["module.py", "config.json"], # Visible items in src (replaces parent list)
            "operable_files": ["module.py", "config.json"], # Allow operations on files in src
            "show_content": True # Show content preview for files in src
        }
        with open(os.path.join(base, "src", "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(src_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'src', 'dirproto.json')}")

        # data directory protocol (Do not inherit, limited visibility, do not show content preview)
        data_proto = {
            "inherit_parent": False, # Do not inherit from root protocol
            "visible_files": ["raw"], # Only the raw subdirectory is visible
            "operable_files": [], # data directory itself and its files are not operable
            "show_content": False # Do not show content preview for files in data (including in raw, unless raw protocol overrides)
        }
        with open(os.path.join(base, "data", "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(data_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'data', 'dirproto.json')}")

        # data/raw directory protocol (Do not inherit, allow csv operations, show content preview)
        data_raw_proto = {
             "inherit_parent": False, # Do not inherit from the data protocol
             "visible_files": ["data1.csv"],
             "operable_files": ["data1.csv"],
             "show_content": True # Show content preview for files in data/raw
        }
        with open(os.path.join(base, "data", "raw", "dirproto.json"), 'w', encoding='utf-8') as f:
            json.dump(data_raw_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'data', 'raw', 'dirproto.json')}")

        # docs directory protocol (Visible, do not show content preview)
        docs_proto = {
            "visible_files": ["index.html"],
            "operable_files": [],
            "show_content": True
        }
        with open(os.path.join(base, "docs", "dirproto.json"), 'w', encoding='utf-8') as f:
             json.dump(docs_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'docs', 'dirproto.json')}")

        # tests directory protocol (Visible, show content preview)
        tests_proto = {
            "visible_files": ["test_main.py"],
            "operable_files": ["test_main.py"], # Allow operations on test_main.py
            "show_content": True
        }
        with open(os.path.join(base, "tests", "dirproto.json"), 'w', encoding='utf-8') as f:
             json.dump(tests_proto, f, indent=4, ensure_ascii=False)
        print(f"创建协议: {os.path.join(base, 'tests', 'dirproto.json')}")

        # empty_dir and hidden_dir will not have protocols initially, initialize_protocols will create empty ones

        print("--- 测试环境设置完毕 ---")

    except Exception as e:
        print(f"设置测试环境时出错: {e}", file=sys.stderr)
        # Attempt to clean up in case of error
        # if os.path.exists(base):
        #      print(f"Attempting cleanup of incomplete test environment: {base}")
        #      shutil.rmtree(base)
        raise # Re-raise the exception so the caller knows setup failed

if __name__ == "__main__":
    TEST_DIR_NAME = "project_proto_test_1"
    # Create the test directory in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    TEST_DIR = os.path.join(script_dir, TEST_DIR_NAME)

    try:
        # 1. Set up the test environment
        setup_test_environment(TEST_DIR)

        # 2. Initialize the manager
        print("\n--- 步骤 2: 初始化 DirProtoManager ---")
        manager = DirProtoManager(TEST_DIR)

        # 3. Initialize protocol files (Ensure dirproto.json exists in all directories)
        print("\n--- 步骤 3: 初始化协议文件 (For directories without dirproto.json) ---")
        # initialize_protocols will create empty {} for empty_dir and hidden_dir
        manager.initialize_protocols()

        # 4. Load all protocols
        print("\n--- 步骤 4: 加载协议 ---")
        manager.load_protocols()
        print(f"DEBUG: Protocols loaded after Step 4. Keys: {list(manager.protocols.keys())}")


        # 5. Display the initial visible directory tree (with content preview)
        print("\n--- 步骤 5: 展示初始可见目录树 (显示内容预览) ---")
        manager.display_tree(show_lines=5) # Limit content display to max 5 lines

        # 6. Execute some commands
        print("\n--- 步骤 6: 执行命令 ---")
        # Successful operations (operable in root)
        manager.execute_command("README.md += \"\\n## 更新说明\\n这是新增的内容。\"") # Append content
        manager.execute_command("main.py = \"print('Hello again')\"") # Overwrite content
        # manager.execute_command("README.md ×") # Temporarily keep to see content change later
        # Failed operations (not operable in root according to root protocol)
        manager.execute_command(".gitignore ×") # Not visible and not operable
        manager.execute_command("binary_file.dat = \"Should not work\"") # Not visible and not operable (and is binary)
        # Failed operation (accessing file in hidden directory, parent directory not visible leading to path resolution/visibility check failure)
        manager.execute_command("hidden_dir/secret.txt = \"New secret\"") # hidden_dir not visible, secret.txt is also not visible

        # Successful operations (operable in src according to src protocol)
        # These failed in your previous output, check debug prints now
        manager.execute_command("src/module.py = \"# Rewritten module\\ndef new_func(): return 1\\n\"")
        # src/config.json is visible and operable. Move operation only checks source operable.
        # Note: After moving to data dir, data's protocol applies (which is no content preview)
        manager.execute_command("src/config.json -> data/config_moved.json")

        # Successful operations (operable in data/raw according to data/raw protocol)
        # This failed in your previous output, check debug prints now
        manager.execute_command("data/raw/data1.csv += \"Extra line\\n\"") # Append a line

        # Failed operation (docs directory has protocol, but index.html is not operable)
        manager.execute_command("docs/index.html ×")

        # Failed operation: Creating a new file where the name is not in operable_files
        # In data/raw, only data1.csv is in operable_files
        manager.execute_command("data/raw/new_file.txt = \"This should fail\"") # operable_files does not include new_file.txt

        # Move main.py to tests directory (main.py is operable in root)
        # The protocol of the tests directory does not affect main.py's permission to be moved *as a source*.
        # Note: After moving, main_moved.py is in the tests directory and is subject to tests protocol for visibility and operability.
        manager.execute_command("main.py -> tests/main_moved.py")

        # Delete README.md now
        manager.execute_command("README.md ×")


        # 7. Reload protocols (because files were added/deleted/moved, protocol environment might have changed)
        print("\n--- 步骤 7: 重新加载协议 ---")
        manager.load_protocols() # Must reload to see if changed/new files are still visible/operable
        print(f"DEBUG: Protocols reloaded after Step 7. Keys: {list(manager.protocols.keys())}")


        # 8. Display the directory tree again to see changes and content display
        print("\n--- 8: 展示操作后的可见目录树 ---")
        manager.display_tree(show_lines=5) # Again limit content to max 5 lines

        # 9. Test the new read_file_content method (simulating AI needing full content)
        print("\n--- 步骤 9: 测试 read_file_content 方法 ---")

        print("\n尝试读取可见文件 (data/raw/data1.csv):")
        content_data1_csv = manager.read_file_content("data/raw/data1.csv")
        if content_data1_csv is not None: # Check for None to handle errors or binary files gracefully
             print("成功读取 data1.csv:")
             print(content_data1_csv)
        else:
             print("无法读取 data1.csv")


        print("\n尝试读取可见文件 (tests/main_moved.py):")
        # According to tests directory protocol (visible_files only has "test_main.py"), main_moved.py is NOT visible, so this should fail
        content_main_moved = manager.read_file_content("tests/main_moved.py")
        if content_main_moved is not None:
             print("成功读取 tests/main_moved.py:")
             print(content_main_moved)
        else:
             print("无法读取 tests/main_moved.py")


        print("\n尝试读取不可见文件 (.gitignore):")
        content_gitignore = manager.read_file_content(".gitignore") # Should fail (not visible)
        if content_gitignore is not None:
             print(".gitignore 内容:")
             print(content_gitignore)
        else:
             print("无法读取 .gitignore")


        print("\n尝试读取二进制文件 (binary_file.dat):")
        # Binary file is not visible in root protocol, so this should fail the visibility check first
        content_binary = manager.read_file_content("binary_file.dat")
        # Check if it's the binary identifier or None (due to visibility failure)
        if content_binary is not None:
             print(f"二进制文件内容: {content_binary}") # Should print the identifier string if visible, else None
        else:
             print("无法读取 binary_file.dat")


        print("\n尝试读取已删除文件 (README.md):")
        content_readme = manager.read_file_content("README.md") # Should fail (does not exist)
        if content_readme is not None:
             print("README.md 内容:")
             print(content_readme)
        else:
             print("无法读取 README.md")


        print("\n尝试读取隐藏目录中的文件 (hidden_dir/secret.txt):")
        content_secret = manager.read_file_content("hidden_dir/secret.txt") # hidden_dir is not visible, so secret.txt is also not visible and should fail
        if content_secret is not None:
             print("hidden_dir/secret.txt 内容:")
             print(content_secret)
        else:
             print("无法读取 hidden_dir/secret.txt")


    except Exception as main_e:
        print(f"\n主程序执行过程中发生错误: {main_e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

    finally:
        # Clean up test environment
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