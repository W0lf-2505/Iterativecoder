# app/executor/executor.py

from typing import Dict, Any

from app.tools.registry import ToolRegistry
from app.schema.tools_response import build_response
import os
import inspect


class Executor:

    def __init__(self):
        self.registry = ToolRegistry()
        self.workspace = os.path.join(os.getcwd(), "workspace")

    def _inject_project_path(self, input_data: dict) -> dict:
        # Work on a COPY (important)
        input_data = dict(input_data)

        project = input_data.get("project")
        

        if project:
            base_path = os.path.join(self.workspace, "projects", project)
            os.makedirs(base_path, exist_ok=True)

            
        else:
            base_path = os.path.join(self.workspace, "temp")

        input_data["cwd"] = base_path

        if "file_path" in input_data and input_data["file_path"]:
            input_data["file_path"] = os.path.join(
                    base_path,
                    input_data["file_path"]
                )
            
        if "directory_path" in input_data and input_data["directory_path"]:
            input_data["directory_path"] = os.path.join(
                base_path,
                input_data["directory_path"]
            )
        
        if "command" in input_data:
            input_data["command"] = f'{input_data["command"]}'

        input_data.pop("project", None)

        return input_data

    def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a validated action
        """

        tool_name = action.get("action")
        input_data = action.get("input", {})
        input_data = self._inject_project_path(input_data)

        tool_fn = self.registry.get_tool(tool_name)

        if not tool_fn:
            return build_response(
                tool=tool_name,
                input_data=input_data,
                stderr=f"Tool '{tool_name}' not found",
                exit_code=1,
                error_type="ToolNotFound",
                error_message=f"{tool_name} is not registered",
            )

        try:

            sig = inspect.signature(tool_fn)
            valid_args = sig.parameters.keys()

            filtered_input = {
                k: v for k, v in input_data.items()
                if k in valid_args
            }

            result = tool_fn(**filtered_input)
            return result

        except Exception as e:
            return build_response(
                tool=tool_name,
                input_data=input_data,
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e),
            )