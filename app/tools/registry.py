# app/tools/registry.py

from typing import Callable, Dict, Any, Optional

from app.tools.terminal_tools import TerminalTools
from app.tools.file_tools import FileTools
from app.tools.base_tool import BaseTool
from app.tools.test_tools import run_tests


class ToolRegistry:

    def __init__(self):

        # ✅ Create instances ONCE
        self.terminal_tools = TerminalTools()
        self.file_tools = FileTools()
        self.base_tools = BaseTool()

        # 🔑 Registry
        self._registry: Dict[str, Dict[str, Dict[str, Any]]] = {
            "terminal_tools": {
                "run_command": {
                    "function": self.terminal_tools.run_command,
                    "description": "Execute a shell command",
                    "args": ["command","cwd"]
                },
                "install_package": {
                    "function": self.terminal_tools.install_package,
                    "description": "Install a Python package",
                    "args": ["package_name"]
                },
                "create_virtual_environment": {
                    "function": self.terminal_tools.create_virtual_environment,
                    "description": "Create virtual environment",
                    "args": ["env_name"]
                },
                "activate_virtual_environment": {
                    "function": self.terminal_tools.activate_virtual_environment,
                    "description": "Activate virtual environment",
                    "args": ["env_name"]
                },
                "deactivate_virtual_environment": {
                    "function": self.terminal_tools.deactivate_virtual_environment,
                    "description": "Deactivate virtual environment",
                    "args": []
                },
                "run_in_container": {
                    "function": self.terminal_tools.run_in_container,
                    "description": "Run command in container",
                    "args": ["container_name", "command"]
                },
            },

            "base_tools": {
                "search_web": {
                    "function": self.base_tools.search_web,
                    "description": "Search the web",
                    "args": ["query"]
                },
                "store_memory": {
                    "function": self.base_tools.store_memory,
                    "description": "Store memory",
                    "args": ["key", "value"]
                },
                "retrieve_memory": {
                    "function": self.base_tools.retrieve_memory,
                    "description": "Retrieve memory",
                    "args": ["query"]
                },
            },

            "test_tools": {
                "run_tests": {
                    "function": run_tests,
                    "description": "Run project tests",
                    "args": []
                }
            },

            "file_tools": {
                "write_to_file": {
                    "function": self.file_tools.write_to_file,
                    "description": "Write content to file",
                    "args": ["file_path", "data"]
                },
                "read_from_file": {
                    "function": self.file_tools.read_from_file,
                    "description": "Read file content",
                    "args": ["file_path"]
                },
                "append_to_file": {
                    "function": self.file_tools.append_to_file,
                    "description": "Append content to file",
                    "args": ["file_path", "data"]
                },
                "delete_file": {
                    "function": self.file_tools.delete_file,
                    "description": "Delete file",
                    "args": ["file_path"]
                },
                "list_files_in_directory": {
                    "function": self.file_tools.list_files_in_directory,
                    "description": "List files in directory",
                    "args": ["directory_path"]
                },
                "create_directory": {
                    "function": self.file_tools.create_directory,
                    "description": "Create directory",
                    "args": ["directory_path"]
                },
                "delete_directory": {
                    "function": self.file_tools.delete_directory,
                    "description": "Delete directory",
                    "args": ["directory_path"]
                }
            }
        }

        # 🔁 Flattened lookup
        self._flat_registry: Dict[str, Callable] = {}
        self._build_flat_registry()

    # =========================
    # 🔧 Internal
    # =========================

    def _build_flat_registry(self):
        for category, tools in self._registry.items():
            for name, meta in tools.items():
                self._flat_registry[name] = meta["function"]

    # =========================
    # 🔍 Public API
    # =========================

    def get_tool(self, tool_name: str) -> Optional[Callable]:
        return self._flat_registry.get(tool_name)

    def list_tools(self):
        return list(self._flat_registry.keys())

    def list_by_category(self, category: str):
        return list(self._registry.get(category, {}).keys())

    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        for tools in self._registry.values():
            if tool_name in tools:
                return tools[tool_name]
        return None