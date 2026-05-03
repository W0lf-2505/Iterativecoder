# app/tools/base_tool.py

import subprocess
from typing import Dict
from app.schema.tools_response import build_response


class BaseTool:

    #  Static in-memory store (shared globally)
    MEMORY: Dict[str, str] = {}

    #  Allowed commands
    ALLOWED_COMMANDS = ["python", "pip", "pytest", "curl", "docker"]

    BLOCKED_PATTERNS = [
        "rm -rf", "del ", "shutdown", "reboot",
        "&&", "||", ";",
        "..", "/etc", "C:\\Windows"
    ]

    # =========================
    # 🔍 SANITY CHECKS
    # =========================

    @staticmethod
    def command_sanity_check(command: str) -> bool:
        if any(bad in command.lower() for bad in BaseTool.BLOCKED_PATTERNS):
            raise ValueError("Dangerous command detected")

        base_cmd = command.split()[0]

        if base_cmd not in BaseTool.ALLOWED_COMMANDS:
            raise ValueError(f"Command '{base_cmd}' not allowed")

        return True

    @staticmethod
    def path_sanity_check(path: str) -> bool:
        if any(bad in path for bad in BaseTool.BLOCKED_PATTERNS):
            raise ValueError("Dangerous file path detected")

        return True

    # =========================
    # 🌐 BASE TOOLS
    # =========================

    @staticmethod
    def search_web(query: str):
        if not query:
            raise ValueError("Search query cannot be empty")

        command = f"curl -s \"https://www.google.com/search?q={query}\""

        try:
            BaseTool.command_sanity_check(command)

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )

            return build_response(
                tool="search_web",
                input_data={"query": query},
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except Exception as e:
            return build_response(
                tool="search_web",
                input_data={"query": query},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )


    @staticmethod
    def store_memory(key: str, value: str):
        if not key or not value:
            raise ValueError("Memory key/value cannot be empty")

        if len(key) > 100 or len(value) > 1000:
            raise ValueError("Memory too large")

        BaseTool.MEMORY[key] = value

        return build_response(
            tool="store_memory",
            input_data={"key": key},
            stdout=f"Stored under key: {key}",
            exit_code=0
        )

    @staticmethod
    def retrieve_memory(query: str):
        return build_response(
            tool="retrieve_memory",
            input_data={"query": query},
            stdout=BaseTool.MEMORY.get(query, "No memory found"),
            exit_code=0
        )
    
    def analyze_error(self, error_message):
        
        from app.agent.debugger import DebuggerLLM
        self.llm = DebuggerLLM()
        response = self.llm.generate(error_message)

        return build_response(
            tool="analyze_error",
            input_data={"error": error_message},
            stdout=response,
            exit_code=0
        )