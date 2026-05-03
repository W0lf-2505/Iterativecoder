# app/executor/validator.py

from typing import Dict, Any

from app.tools.registry import ToolRegistry

registry = ToolRegistry()


ALLOWED_TOOLS = [
    "write_to_file",
    "read_from_file",
    "list_files_in_directory",
    "run_command",
    "run_tests",
]


BLOCKED_COMMANDS = [
    "rm -rf",
    "del ",
    "shutdown",
    "reboot",
]


def validate_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parsed action before execution
    """

    tool = action.get("action")
    input_data = action.get("input", {})
    

    
    tool_fn = registry.get_tool(tool)

    if not tool_fn:
        raise ValueError(f"Tool '{tool}' is not allowed")
    

    # 🔒 Extra validation for terminal commands
    if tool == "run_command":
        command = input_data.get("command", "")
            
        if "python -c" in command:
            raise ValueError("Inline python execution not allowed")

        for blocked in BLOCKED_COMMANDS:
            if blocked in command.lower():
                raise ValueError(f"Blocked command detected: {blocked}")

    return action