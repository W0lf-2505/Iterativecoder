from pydantic import BaseModel
from typing import Optional, Dict, Any

class Output(BaseModel):
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0


class Error(BaseModel):
    type: Optional[str] = None
    message: Optional[str] = None


class ToolResponse(BaseModel):
    status: str  # "success" or "error"
    tool: str
    input: Dict[str, Any]
    output: Output
    error: Error
    meta: Dict[str, Any] = {}

def build_response(
    tool: str,
    input_data: Dict[str, Any],
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> dict:

    response = ToolResponse(
        status="success" if exit_code == 0 else "error",
        tool=tool,
        input=input_data,
        output=Output(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        ),
        error=Error(
            type=error_type,
            message=error_message,
        ),
        meta=meta or {},
    )

    return response.dict()